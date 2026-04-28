"""Routes for stores, country, and filter-option lookups."""
from __future__ import annotations

from fastapi import APIRouter, Query, Request

from app.schemas import FilterOptions, StoreSummary
from app.services.assortment import AssortmentService


router = APIRouter(tags=["stores"])


def _service(request: Request) -> AssortmentService:
    return request.app.state.assortment


@router.get("/stores", response_model=list[StoreSummary])
async def list_stores(request: Request) -> list[StoreSummary]:
    """Return all non-agent Systembolaget stores."""
    return _service(request).get_store_summaries()


@router.get("/countries", response_model=list[str])
async def list_countries(
    request: Request,
    store_ids: list[str] | None = Query(default=None, alias="storeIds"),
) -> list[str]:
    """Return distinct countries available in the assortment."""
    return _service(request).get_unique_countries(store_ids)


@router.get("/filter-options", response_model=FilterOptions)
async def filter_options(
    request: Request,
    store_ids: list[str] | None = Query(default=None, alias="storeIds"),
    wine_types: list[str] | None = Query(default=None, alias="wineTypes"),
) -> FilterOptions:
    """Return distinct values for all dropdown-style filters.

    `wineTypes` restricts the returned `tasteProfiles` to profiles that
    actually exist for those wine types.
    """
    raw = _service(request).get_filter_options(
        site_ids=store_ids, wine_types=wine_types
    )
    return FilterOptions(**raw)
