"""Async client for talking to OpenAI's chat completions API."""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.errors import OpenAIError, OpenAIUnavailable


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "Du är en sommelier som rekommenderar VIN från Systembolaget till en "
    "svensk kund. Du får en numrerad lista med viner. Användaren beskriver "
    "vad hen ska äta eller dricka till, och DU SKA VÄLJA UT 3 VINER FRÅN "
    "LISTAN som passar bäst.\n\n"
    "VIKTIGT:\n"
    "- Du ska INTE ge recept, ingredienser eller tillagningsanvisningar.\n"
    "- Du ska INTE ge maträtter, mat-tips eller kommentarer om maten.\n"
    "- Du ska ENBART välja viner från listan och motivera valen kort.\n\n"
    "Svaret måste följa exakt detta JSON-schema:\n"
    "{\n"
    '  "intro": "<en kort mening på svenska som introducerar valen>",\n'
    '  "picks": [\n'
    '    {"id": <id från listan>, "motivation": "<1-2 meningar på svenska>"},\n'
    '    {"id": <id från listan>, "motivation": "<1-2 meningar på svenska>"},\n'
    '    {"id": <id från listan>, "motivation": "<1-2 meningar på svenska>"}\n'
    "  ]\n"
    "}\n\n"
    "Exempel på korrekt svar:\n"
    "{\n"
    '  "intro": "Här är tre rödviner som passar din pasta.",\n'
    '  "picks": [\n'
    '    {"id": 12, "motivation": "Fyllig smak med fatkaraktär passar köttsåsen."},\n'
    '    {"id": 34, "motivation": "Fruktigt och balanserat, ett säkert val."},\n'
    '    {"id": 56, "motivation": "Mjuka tanniner som ramar in tomatsåsen."}\n'
    "  ]\n"
    "}\n\n"
    "Reglerna är absoluta. Skriv inte ett enda tecken utanför JSON-objektet."
)


# JSON Schema sent to OpenAI so the model is forced to obey output shape.
RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "intro": {"type": "string"},
        "picks": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "motivation": {"type": "string"},
                },
                "required": ["id", "motivation"],
            },
        },
    },
    "required": ["intro", "picks"],
}


def number_wines_for_prompt(
    wines: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Add a small numeric ``id`` (1..N) to each wine for prompting.

    Small integer IDs are far easier for a 7B model to copy verbatim than
    7-digit Systembolag article numbers.
    """
    out = []
    for idx, wine in enumerate(wines, start=1):
        item = {"id": idx}
        # Only include the most useful fields so the prompt stays compact.
        for key in (
            "productNameBold",
            "productNameThin",
            "producerName",
            "vintage",
            "country",
            "originLevel1",
            "categoryLevel2",
            "categoryLevel3",
            "price",
            "volume",
            "alcoholPercentage",
        ):
            value = wine.get(key)
            if value is not None and value != "":
                item[key] = value
        out.append(item)
    return out


def build_user_message(
    numbered_wines: list[dict[str, Any]],
    user_prompt: str,
) -> str:
    """Construct the user-side message sent to the LLM."""
    wines_json = json.dumps(numbered_wines, ensure_ascii=False)
    return (
        f"Vinlista ({len(numbered_wines)} viner):\n{wines_json}\n\n"
        f"Kunden vill ha vinrekommendationer för: {user_prompt}\n\n"
        "Välj 3 viner från listan ovan som passar. Svara med JSON enligt "
        "schemat (intro + picks med id och motivation). Inga recept eller "
        "matlagningsråd."
    )


class OpenAIClient:
    """Lightweight async wrapper around OpenAI's chat completions API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 180.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key.strip()
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout, connect=5.0),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

    @property
    def model(self) -> str:
        return self._model

    async def aclose(self) -> None:
        await self._client.aclose()

    async def request_recommendations(
        self,
        user_prompt: str,
        numbered_wines: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Ask OpenAI for structured wine recommendations.

        Raises:
            OpenAIUnavailable: connection refused / DNS / timeout.
            OpenAIError: any other failure (HTTP, malformed JSON, ...).
        """
        if not self._api_key:
            raise OpenAIError(
                "OPENAI_API_KEY saknas. Lägg till den i backend/.env."
            )

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_message(numbered_wines, user_prompt),
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "wine_recommendations",
                    "schema": RESPONSE_SCHEMA,
                    "strict": True,
                },
            },
            "temperature": 0.2,
        }

        try:
            response = await self._client.post("/chat/completions", json=payload)
        except httpx.ConnectError as exc:
            raise OpenAIUnavailable(
                f"Could not connect to OpenAI at {self._base_url}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OpenAIError(f"HTTP error while talking to OpenAI: {exc}") from exc

        if response.status_code >= 400:
            raise OpenAIError(
                f"OpenAI responded {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise OpenAIError(
                f"OpenAI response was not JSON: {response.text}"
            ) from exc

        choices = data.get("choices") or []
        message = choices[0].get("message") if choices and isinstance(choices[0], dict) else {}
        content: Any = message.get("content") if isinstance(message, dict) else ""
        if isinstance(content, list):
            content = "".join(
                str(part.get("text", ""))
                for part in content
                if isinstance(part, dict)
            )
        if not isinstance(content, str) or not content.strip():
            raise OpenAIError("OpenAI returned an empty message")

        logger.info("LLM raw response (%d chars): %s", len(content), content)

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.warning("LLM produced invalid JSON despite schema mode: %s", content)
            raise OpenAIError(
                "LLM produced invalid JSON. Try a stronger model or rephrase."
            ) from exc
