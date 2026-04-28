"""Tests for wine route helpers (no LLM/network)."""
from __future__ import annotations

from app.routes.wines import (
    _build_recommendations,
    _coerce_int,
    _extract_picks,
    _systembolaget_url,
)


WINE_A = {
    "productNumber": "1001",
    "productNameBold": "Bordeaux",
    "categoryLevel2": "Rött vin",
}
WINE_B = {
    "productNumber": "2001",
    "productNameBold": "Cava",
    "categoryLevel2": "Mousserande",
}

WINES_BY_ID = {1: WINE_A, 2: WINE_B}
WINES_BY_PN = {"1001": WINE_A, "2001": WINE_B}


def test_build_recommendations_uses_numeric_id() -> None:
    picks = [
        {"id": 1, "motivation": "Funkar fint."},
        {"id": 2, "motivation": "Bubblig och bra."},
    ]
    recs, notes = _build_recommendations(picks, WINES_BY_ID, WINES_BY_PN)

    assert [r.wine.productNumber for r in recs] == ["1001", "2001"]
    assert notes == []
    assert recs[0].systembolagetUrl.endswith("q=1001")


def test_build_recommendations_falls_back_to_product_number() -> None:
    picks = [{"productNumber": "2001", "motivation": "Funkar."}]
    recs, notes = _build_recommendations(picks, WINES_BY_ID, WINES_BY_PN)
    assert [r.wine.productNumber for r in recs] == ["2001"]
    assert notes == []


def test_build_recommendations_drops_unknown() -> None:
    picks = [
        {"id": 1, "motivation": "Bra."},
        {"id": 999, "motivation": "Hallucination."},
        {"productNumber": "9999", "motivation": "Hallucination."},
    ]
    recs, notes = _build_recommendations(picks, WINES_BY_ID, WINES_BY_PN)
    assert [r.wine.productNumber for r in recs] == ["1001"]
    assert len(notes) == 2


def test_build_recommendations_dedupes() -> None:
    picks = [
        {"id": 1, "motivation": "A"},
        {"productNumber": "1001", "motivation": "Samma vin"},
    ]
    recs, _ = _build_recommendations(picks, WINES_BY_ID, WINES_BY_PN)
    assert len(recs) == 1


def test_extract_picks_handles_various_shapes() -> None:
    item = {"id": 1}
    assert _extract_picks({"picks": [item]}) == [item]
    assert _extract_picks({"recommendations": [item]}) == [item]
    assert _extract_picks({"wines": [item]}) == [item]
    assert _extract_picks([item]) == [item]
    assert _extract_picks({"output": {"picks": [item]}}) == [item]
    assert _extract_picks({}) == []
    assert _extract_picks("garbage") == []


def test_coerce_int_accepts_strings_and_floats() -> None:
    assert _coerce_int(3) == 3
    assert _coerce_int("3") == 3
    assert _coerce_int("vin nr 17") == 17
    assert _coerce_int(2.0) == 2
    assert _coerce_int(2.5) is None
    assert _coerce_int(True) is None
    assert _coerce_int(None) is None


def test_systembolaget_url_format() -> None:
    assert _systembolaget_url("2013601") == (
        "https://www.systembolaget.se/sortiment/sok/?q=2013601"
    )
