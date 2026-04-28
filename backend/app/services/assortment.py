"""In-memory store of Systembolaget assortment data.

Loads JSON files from the configured `assortments` directory and exposes
fast filtering, deduplication and country/wine queries.
"""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Iterable

from app.errors import StoreNotFound
from app.schemas import Range, StoreSummary, Wine


logger = logging.getLogger(__name__)


# Fields that are kept when serialising a wine for the frontend / LLM.
_WINE_FIELDS: tuple[str, ...] = (
    "productNumber",
    "productNameBold",
    "productNameThin",
    "producerName",
    "vintage",
    "country",
    "originLevel1",
    "categoryLevel2",
    "categoryLevel3",
    "assortmentText",
    "price",
    "volume",
    "alcoholPercentage",
    "productLaunchDate",
    "isCompletelyOutOfStock",
    "isTemporaryOutOfStock",
)


def fix_mojibake(value: str) -> str:
    """Repair strings that were UTF-8 bytes accidentally decoded as Latin-1.

    Some of the source JSON files were exported with bytes that look like
    ``F\\u00c3\\u00a4lt\\u00c3\\u00b6versten`` instead of ``Fältöversten``.
    Re-encoding as Latin-1 and decoding as UTF-8 reverses the damage when
    it occurred. If the string is already correct the round-trip raises
    an exception and we return the original unchanged.
    """
    try:
        repaired = value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value
    return repaired


def _clean(value: Any) -> Any:
    """Recursively apply :func:`fix_mojibake` to any strings inside a value."""
    if isinstance(value, str):
        return fix_mojibake(value)
    if isinstance(value, list):
        return [_clean(item) for item in value]
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    return value


def _project_wine(raw: dict[str, Any]) -> dict[str, Any]:
    """Pick only the fields we care about and convert numerics."""
    wine: dict[str, Any] = {}
    for field in _WINE_FIELDS:
        value = raw.get(field)
        wine[field] = fix_mojibake(value) if isinstance(value, str) else value

    # Coerce numerics so range filtering becomes reliable.
    for numeric in ("price", "volume", "alcoholPercentage"):
        value = wine[numeric]
        try:
            wine[numeric] = float(value) if value is not None else None
        except (TypeError, ValueError):
            wine[numeric] = None

    # Coerce booleans (some sources use 0/1 or strings).
    for flag in ("isCompletelyOutOfStock", "isTemporaryOutOfStock"):
        wine[flag] = bool(wine.get(flag))

    if wine.get("productNumber") is not None:
        wine["productNumber"] = str(wine["productNumber"])

    return wine


class AssortmentService:
    """Lazy in-memory cache of store-level assortments."""

    def __init__(self, assortments_dir: Path) -> None:
        self._dir = Path(assortments_dir)
        self._stores_cache: list[dict[str, Any]] | None = None
        self._assortment_cache: dict[str, list[dict[str, Any]]] = {}
        self._lock = threading.Lock()

    # --- Stores -------------------------------------------------------

    def load_stores(self) -> list[dict[str, Any]]:
        """Load (and cache) the list of non-agent stores."""
        if self._stores_cache is not None:
            return self._stores_cache

        path = self._dir / "stores.json"
        if not path.exists():
            logger.error("stores.json not found at %s", path)
            self._stores_cache = []
            return self._stores_cache

        try:
            with path.open("r", encoding="utf-8") as f:
                raw_stores = json.load(f)
        except json.JSONDecodeError:
            logger.exception("Failed to decode stores.json")
            self._stores_cache = []
            return self._stores_cache

        non_agent = [
            _clean(s) for s in raw_stores if not s.get("isAgent", False)
        ]
        logger.info("Loaded %d non-agent stores", len(non_agent))
        self._stores_cache = non_agent
        return self._stores_cache

    def get_store_summaries(self) -> list[StoreSummary]:
        return [StoreSummary.from_raw(s) for s in self.load_stores()]

    # --- Assortments --------------------------------------------------

    def _load_assortment(self, site_id: str) -> list[dict[str, Any]]:
        if site_id in self._assortment_cache:
            return self._assortment_cache[site_id]

        with self._lock:
            if site_id in self._assortment_cache:
                return self._assortment_cache[site_id]

            path = self._dir / f"{site_id}.json"
            if not path.exists():
                raise StoreNotFound(f"Assortment file for store '{site_id}' not found")

            try:
                with path.open("r", encoding="utf-8") as f:
                    products = json.load(f)
            except json.JSONDecodeError as exc:
                raise StoreNotFound(
                    f"Assortment file for store '{site_id}' is invalid JSON"
                ) from exc

            wines = [_project_wine(p) for p in products]
            self._assortment_cache[site_id] = wines
            logger.info(
                "Loaded %d wines from store %s", len(wines), site_id
            )
            return wines

    def _resolve_site_ids(self, site_ids: Iterable[str] | None) -> list[str]:
        if site_ids is None:
            return [
                p.stem
                for p in self._dir.glob("*.json")
                if p.stem != "stores"
            ]
        return list(site_ids)

    def get_unique_countries(self, site_ids: Iterable[str] | None = None) -> list[str]:
        """Return a sorted list of distinct countries across the given stores."""
        return self._collect_distinct(
            self._resolve_site_ids(site_ids), field="country"
        )

    def _collect_distinct(
        self,
        site_ids: list[str],
        field: str,
        wine_types: list[str] | None = None,
    ) -> list[str]:
        """Collect distinct non-empty string values for a given wine field."""
        type_filter = set(wine_types) if wine_types else None
        values: set[str] = set()
        for site_id in site_ids:
            try:
                for wine in self._load_assortment(site_id):
                    if type_filter and wine.get("categoryLevel2") not in type_filter:
                        continue
                    raw = wine.get(field)
                    if isinstance(raw, str) and raw:
                        values.add(raw)
            except StoreNotFound:
                continue
        return sorted(values)

    def get_filter_options(
        self,
        site_ids: Iterable[str] | None = None,
        wine_types: list[str] | None = None,
    ) -> dict[str, list[str]]:
        """Return distinct values for the dropdown-style filters.

        ``wine_types`` (matched against ``categoryLevel2``) restricts the
        ``taste_profiles`` result to profiles that actually exist for the
        chosen wine types.
        """
        ids = self._resolve_site_ids(site_ids)
        return {
            "wineTypes": self._collect_distinct(ids, "categoryLevel2"),
            "tasteProfiles": self._collect_distinct(
                ids, "categoryLevel3", wine_types=wine_types
            ),
            "assortmentTypes": self._collect_distinct(ids, "assortmentText"),
            "countries": self._collect_distinct(ids, "country"),
        }

    def filter_wines(
        self,
        site_ids: list[str],
        countries: list[str] | None = None,
        price_range: Range | None = None,
        volume_range: Range | None = None,
        wine_types: list[str] | None = None,
        taste_profiles: list[str] | None = None,
        assortment_types: list[str] | None = None,
        alcohol_range: Range | None = None,
        in_stock_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Return wines from the given stores that pass all filters.

        Deduplicates by ``productNumber`` in O(n) using a set.
        """
        if not site_ids:
            return []

        seen: set[str] = set()
        result: list[dict[str, Any]] = []

        country_filter = set(countries) if countries else None
        wine_type_filter = set(wine_types) if wine_types else None
        taste_filter = set(taste_profiles) if taste_profiles else None
        assortment_filter = set(assortment_types) if assortment_types else None

        for site_id in site_ids:
            wines = self._load_assortment(site_id)
            for wine in wines:
                pid = wine.get("productNumber")
                if not pid or pid in seen:
                    continue

                if country_filter and wine.get("country") not in country_filter:
                    continue
                if wine_type_filter and wine.get("categoryLevel2") not in wine_type_filter:
                    continue
                if taste_filter and wine.get("categoryLevel3") not in taste_filter:
                    continue
                if assortment_filter and wine.get("assortmentText") not in assortment_filter:
                    continue

                if in_stock_only and (
                    wine.get("isCompletelyOutOfStock")
                    or wine.get("isTemporaryOutOfStock")
                ):
                    continue

                if price_range is not None:
                    price = wine.get("price")
                    if price is None or not (price_range.min <= price <= price_range.max):
                        continue

                if volume_range is not None:
                    volume = wine.get("volume")
                    if volume is None or not (volume_range.min <= volume <= volume_range.max):
                        continue

                if alcohol_range is not None:
                    alcohol = wine.get("alcoholPercentage")
                    if alcohol is None or not (
                        alcohol_range.min <= alcohol <= alcohol_range.max
                    ):
                        continue

                seen.add(pid)
                result.append(wine)

        logger.info(
            "Filtered %d wines from %d stores "
            "(types=%s, profiles=%s, countries=%s, in_stock=%s)",
            len(result),
            len(site_ids),
            wine_types or "any",
            taste_profiles or "any",
            countries or "any",
            in_stock_only,
        )
        return result

    # --- Helpers for the LLM prompt -----------------------------------

    @staticmethod
    def trim_wines_for_prompt(
        wines: list[dict[str, Any]], limit: int
    ) -> list[dict[str, Any]]:
        """Cap the wines passed to the LLM so prompts stay fast and cheap.

        Spreads the selection across the price range to give the model variety.
        """
        if len(wines) <= limit:
            return wines

        priced = [w for w in wines if w.get("price") is not None]
        unpriced = [w for w in wines if w.get("price") is None]

        priced.sort(key=lambda w: w["price"])
        if not priced:
            return wines[:limit]

        # Take an evenly spaced sample across the price-sorted list.
        step = max(1, len(priced) // limit)
        sampled: list[dict[str, Any]] = priced[::step][:limit]

        if len(sampled) < limit and unpriced:
            sampled.extend(unpriced[: limit - len(sampled)])

        return sampled[:limit]

    @staticmethod
    def to_wine_models(wines: list[dict[str, Any]]) -> list[Wine]:
        return [Wine(**w) for w in wines]
