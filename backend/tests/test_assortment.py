"""Tests for AssortmentService."""
from __future__ import annotations

import pytest

from app.errors import StoreNotFound
from app.schemas import Range
from app.services.assortment import AssortmentService, fix_mojibake


def test_get_store_summaries_filters_agents(service: AssortmentService) -> None:
    summaries = service.get_store_summaries()
    assert [s.siteId for s in summaries] == ["0001"]
    assert summaries[0].displayName == "Test Store 1"


def test_filter_wines_dedupes_across_stores(service: AssortmentService) -> None:
    wines = service.filter_wines(["0001", "0002"])
    product_numbers = sorted(w["productNumber"] for w in wines)
    # 1001 appears in both stores but only once in result
    assert product_numbers == ["1001", "1002", "1003", "2001"]


def test_filter_wines_country_filter(service: AssortmentService) -> None:
    wines = service.filter_wines(["0001", "0002"], countries=["Italien"])
    assert {w["productNumber"] for w in wines} == {"1002", "1003"}


def test_filter_wines_price_range(service: AssortmentService) -> None:
    wines = service.filter_wines(
        ["0001", "0002"],
        price_range=Range(min=100, max=200),
    )
    assert {w["productNumber"] for w in wines} == {"1001", "1002"}


def test_filter_wines_volume_range(service: AssortmentService) -> None:
    wines = service.filter_wines(
        ["0001"],
        volume_range=Range(min=1000, max=2000),
    )
    assert {w["productNumber"] for w in wines} == {"1003"}


def test_filter_wines_unknown_store_raises(service: AssortmentService) -> None:
    with pytest.raises(StoreNotFound):
        service.filter_wines(["does-not-exist"])


def test_get_unique_countries(service: AssortmentService) -> None:
    countries = service.get_unique_countries(["0001", "0002"])
    assert countries == ["Frankrike", "Italien", "Spanien"]


def test_filter_wines_wine_type(service: AssortmentService) -> None:
    wines = service.filter_wines(["0001", "0002"], wine_types=["Vitt vin"])
    assert {w["productNumber"] for w in wines} == {"1003"}


def test_filter_wines_taste_profile(service: AssortmentService) -> None:
    wines = service.filter_wines(
        ["0001", "0002"], taste_profiles=["Fruktigt & Smakrikt"]
    )
    assert {w["productNumber"] for w in wines} == {"1001"}


def test_filter_wines_assortment_type(service: AssortmentService) -> None:
    wines = service.filter_wines(
        ["0001", "0002"], assortment_types=["Fast sortiment"]
    )
    assert {w["productNumber"] for w in wines} == {"1001", "1003", "2001"}


def test_filter_wines_alcohol_range(service: AssortmentService) -> None:
    wines = service.filter_wines(
        ["0001", "0002"], alcohol_range=Range(min=12, max=14)
    )
    assert {w["productNumber"] for w in wines} == {"1001", "1002"}


def test_filter_wines_in_stock_only(service: AssortmentService) -> None:
    wines = service.filter_wines(["0001", "0002"], in_stock_only=True)
    # 1002 (out of stock) and 1003 (temp out of stock) are excluded
    assert {w["productNumber"] for w in wines} == {"1001", "2001"}


def test_filter_wines_combines_filters(service: AssortmentService) -> None:
    wines = service.filter_wines(
        ["0001", "0002"],
        wine_types=["Rött vin"],
        in_stock_only=True,
    )
    assert {w["productNumber"] for w in wines} == {"1001"}


def test_get_filter_options(service: AssortmentService) -> None:
    options = service.get_filter_options(["0001", "0002"])
    assert options["wineTypes"] == ["Mousserande", "Rött vin", "Vitt vin"]
    assert options["countries"] == ["Frankrike", "Italien", "Spanien"]
    assert "Fast sortiment" in options["assortmentTypes"]
    assert "Fruktigt & Smakrikt" in options["tasteProfiles"]


def test_get_filter_options_taste_filtered_by_wine_type(
    service: AssortmentService,
) -> None:
    options = service.get_filter_options(
        ["0001", "0002"], wine_types=["Vitt vin"]
    )
    # Only the white wine's profile should be returned
    assert options["tasteProfiles"] == ["Friskt & Fruktigt"]


def test_trim_wines_for_prompt_caps_count() -> None:
    wines = [{"productNumber": str(i), "price": float(i)} for i in range(100)]
    trimmed = AssortmentService.trim_wines_for_prompt(wines, limit=10)
    assert len(trimmed) == 10
    # Should be sampled across the price range, not just the first 10
    prices = [w["price"] for w in trimmed]
    assert max(prices) > 50  # we got something from the high end


def test_trim_wines_for_prompt_handles_unpriced() -> None:
    wines = [{"productNumber": "x", "price": None}]
    trimmed = AssortmentService.trim_wines_for_prompt(wines, limit=5)
    assert len(trimmed) == 1


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Fältöversten", "Fältöversten"),  # already correct
        ("FÃ¤ltÃ¶versten", "Fältöversten"),  # double-encoded
        ("Stockholms lÃ¤n", "Stockholms län"),
        ("STOCKHOLM", "STOCKHOLM"),  # plain ASCII
        ("CafÃ©", "Café"),  # é mojibake
        ("", ""),
    ],
)
def test_fix_mojibake(raw: str, expected: str) -> None:
    assert fix_mojibake(raw) == expected
