"""Routes for wine recommendations."""
from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import APIRouter, Request

from app.errors import OllamaError, OllamaUnavailable
from app.schemas import AskRequest, AskResponse, Recommendation, Wine
from app.services.assortment import AssortmentService
from app.services.ollama import OllamaClient, number_wines_for_prompt


logger = logging.getLogger(__name__)
router = APIRouter(tags=["wines"])


def _systembolaget_url(product_number: str) -> str:
    """Return a stable URL that points to the product on systembolaget.se."""
    return f"https://www.systembolaget.se/sortiment/sok/?q={product_number}"


# Common keys the LLM sometimes uses instead of "picks".
_PICK_LIST_KEYS = ("picks", "recommendations", "wines", "products", "result")
# Common keys the LLM sometimes uses instead of "id".
_ID_KEYS = ("id", "ID", "Id", "wineId", "wine_id", "index")


def _extract_picks(payload: Any) -> list[dict[str, Any]]:
    """Find the picks array within whatever shape the LLM returned."""
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]
    if not isinstance(payload, dict):
        return []
    for key in _PICK_LIST_KEYS:
        value = payload.get(key)
        if isinstance(value, list):
            return [p for p in value if isinstance(p, dict)]
    # Sometimes the model wraps the whole thing one level deeper.
    for value in payload.values():
        if isinstance(value, dict):
            nested = _extract_picks(value)
            if nested:
                return nested
    return []


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"-?\d+", value)
        if match:
            try:
                return int(match.group())
            except ValueError:
                return None
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _build_recommendations(
    raw_picks: list[dict[str, Any]],
    wines_by_id: dict[int, dict[str, Any]],
    wines_by_product_number: dict[str, dict[str, Any]],
) -> tuple[list[Recommendation], list[str]]:
    """Match the LLM's picks against our trusted wine list.

    Tries (in order):
    1. The numeric "id" the prompt assigned (most reliable).
    2. Any "productNumber"/"product_number" field if the model bypassed ids.
    Drops anything that doesn't resolve and reports it in `notes`.
    """
    out: list[Recommendation] = []
    notes: list[str] = []
    seen: set[str] = set()

    for raw in raw_picks:
        if not isinstance(raw, dict):
            continue

        motivation = str(raw.get("motivation") or raw.get("reason") or "").strip()
        wine: dict[str, Any] | None = None

        # Try id-based lookup first.
        for key in _ID_KEYS:
            if key in raw:
                idx = _coerce_int(raw[key])
                if idx is not None and idx in wines_by_id:
                    wine = wines_by_id[idx]
                    break

        # Fallback: productNumber-style fields.
        if wine is None:
            for key in (
                "productNumber",
                "product_number",
                "productnumber",
                "articleNumber",
                "article_number",
            ):
                if key in raw:
                    pid = str(raw[key]).strip()
                    if pid in wines_by_product_number:
                        wine = wines_by_product_number[pid]
                        break

        if wine is None:
            notes.append(
                f"AI:n föreslog ett vin som inte fanns i listan: {raw}"
            )
            continue

        pid = wine["productNumber"]
        if pid in seen:
            continue
        seen.add(pid)

        out.append(
            Recommendation(
                wine=Wine(**wine),
                motivation=motivation or "Inget motiverande svar.",
                systembolagetUrl=_systembolaget_url(pid),
            )
        )

    return out, notes


@router.post("/ask", response_model=AskResponse)
async def ask(request: Request, body: AskRequest) -> AskResponse:
    """Return structured wine recommendations for the given request."""
    settings = request.app.state.settings
    assortment: AssortmentService = request.app.state.assortment
    ollama: OllamaClient = request.app.state.ollama

    wines = assortment.filter_wines(
        site_ids=body.store_ids,
        countries=body.countries or None,
        wine_types=body.wine_types or None,
        taste_profiles=body.taste_profiles or None,
        assortment_types=body.assortment_types or None,
        price_range=body.price_range,
        volume_range=body.volume_range,
        alcohol_range=body.alcohol_range,
        in_stock_only=body.in_stock_only,
    )

    if not wines:
        return AskResponse(
            intro=(
                "Inga viner matchade dina filter. Prova att vidga "
                "prisintervallet, välja fler butiker eller ta bort några filter."
            ),
            matchedWineCount=0,
        )

    trimmed = AssortmentService.trim_wines_for_prompt(
        wines, settings.max_wines_to_llm
    )
    numbered = number_wines_for_prompt(trimmed)
    logger.info(
        "Asking Ollama with %d/%d wines (cap=%d, ids 1..%d)",
        len(trimmed),
        len(wines),
        settings.max_wines_to_llm,
        len(trimmed),
    )

    wines_by_id: dict[int, dict[str, Any]] = {
        i + 1: w for i, w in enumerate(trimmed)
    }
    wines_by_product_number: dict[str, dict[str, Any]] = {
        w["productNumber"]: w for w in trimmed if w.get("productNumber")
    }

    notes: list[str] = []
    intro = ""
    recommendations: list[Recommendation] = []
    last_error: str | None = None

    # Retry once if the model produces a result that doesn't match the schema.
    # Small models (e.g. Mistral 7B) can ignore the system prompt on the
    # first try, especially if the user message is a recipe or food name.
    for attempt in (1, 2):
        try:
            result = await ollama.request_recommendations(body.prompt, numbered)
        except OllamaUnavailable as exc:
            logger.warning("Ollama unavailable: %s", exc)
            return AskResponse(
                intro=(
                    f"Kunde inte nå Ollama på {settings.ollama_url}. "
                    "Kontrollera att Ollama körs och försök igen."
                ),
                matchedWineCount=len(wines),
                notes=[str(exc)],
            )
        except OllamaError as exc:
            logger.warning("Ollama error (attempt %d): %s", attempt, exc)
            last_error = str(exc)
            continue

        intro = str(result.get("intro", "")).strip()
        raw_picks = _extract_picks(result)

        if not raw_picks:
            logger.warning(
                "LLM returned no picks (attempt %d). Raw result keys: %s",
                attempt,
                list(result.keys()) if isinstance(result, dict) else type(result),
            )

        recommendations, parse_notes = _build_recommendations(
            raw_picks, wines_by_id, wines_by_product_number
        )
        notes.extend(parse_notes)

        if recommendations:
            break

        if attempt == 1:
            notes.append(
                "AI:ns första svar följde inte schemat – försöker igen."
            )

    if not recommendations and not intro:
        intro = (
            "AI:n kunde inte välja några viner från listan – "
            "modellen kan vara för svag för det här jobbet. "
            "Prova en starkare modell (t.ex. llama3.1) eller "
            "skriv om frågan."
        )
        if last_error:
            notes.append(last_error)

    return AskResponse(
        intro=intro,
        recommendations=recommendations,
        matchedWineCount=len(wines),
        notes=notes,
    )
