"""Pydantic models used for request/response validation."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Range(BaseModel):
    min: float = Field(ge=0)
    max: float = Field(ge=0)

    @model_validator(mode="after")
    def _check_min_le_max(self) -> "Range":
        if self.min > self.max:
            raise ValueError("min must be <= max")
        return self


class AskRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(min_length=1, max_length=2000)
    store_ids: list[str] = Field(min_length=1, alias="storeIds")
    countries: list[str] = Field(default_factory=list)
    wine_types: list[str] = Field(default_factory=list, alias="wineTypes")
    taste_profiles: list[str] = Field(default_factory=list, alias="tasteProfiles")
    assortment_types: list[str] = Field(default_factory=list, alias="assortmentTypes")
    price_range: Range = Field(default=Range(min=0, max=5000), alias="priceRange")
    volume_range: Range = Field(default=Range(min=0, max=1500), alias="volumeRange")
    alcohol_range: Range = Field(default=Range(min=0, max=20), alias="alcoholRange")
    in_stock_only: bool = Field(default=True, alias="inStockOnly")


class FilterOptions(BaseModel):
    wineTypes: list[str] = Field(default_factory=list)
    tasteProfiles: list[str] = Field(default_factory=list)
    assortmentTypes: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    """A single wine recommendation, combining a verified wine with a motivation."""

    wine: "Wine"
    motivation: str
    systembolagetUrl: str


class AskResponse(BaseModel):
    """Structured response returned by POST /api/ask."""

    intro: str = ""
    recommendations: list[Recommendation] = Field(default_factory=list)
    matchedWineCount: int = 0
    notes: list[str] = Field(default_factory=list)


class Wine(BaseModel):
    productNumber: str
    productNameBold: str | None = None
    productNameThin: str | None = None
    producerName: str | None = None
    vintage: str | None = None
    country: str | None = None
    originLevel1: str | None = None
    categoryLevel2: str | None = None
    categoryLevel3: str | None = None
    assortmentText: str | None = None
    price: float | None = None
    volume: float | None = None
    alcoholPercentage: float | None = None
    productLaunchDate: str | None = None
    isCompletelyOutOfStock: bool = False
    isTemporaryOutOfStock: bool = False


class StoreSummary(BaseModel):
    siteId: str
    displayName: str | None = None
    alias: str | None = None
    city: str | None = None
    county: str | None = None

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "StoreSummary":
        return cls(
            siteId=str(raw.get("siteId", "")),
            displayName=raw.get("displayName"),
            alias=raw.get("alias"),
            city=raw.get("city"),
            county=raw.get("county"),
        )


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
