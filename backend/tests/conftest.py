"""Shared pytest fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.assortment import AssortmentService


@pytest.fixture
def tmp_assortments(tmp_path: Path) -> Path:
    """A temporary assortments directory with two stores and one stores.json."""
    (tmp_path / "stores.json").write_text(
        json.dumps(
            [
                {
                    "siteId": "0001",
                    "alias": "Test 1",
                    "displayName": "Test Store 1",
                    "city": "Stockholm",
                    "county": "Stockholms län",
                    "isAgent": False,
                },
                {
                    "siteId": "9999",
                    "alias": "Agent",
                    "isAgent": True,
                },
            ]
        ),
        encoding="utf-8",
    )

    (tmp_path / "0001.json").write_text(
        json.dumps(
            [
                {
                    "productNumber": "1001",
                    "productNameBold": "Bordeaux",
                    "productNameThin": "Reserve",
                    "producerName": "Chateau A",
                    "country": "Frankrike",
                    "originLevel1": "Bordeaux",
                    "categoryLevel2": "Rött vin",
                    "categoryLevel3": "Fruktigt & Smakrikt",
                    "assortmentText": "Fast sortiment",
                    "alcoholPercentage": 13.5,
                    "vintage": "2018",
                    "price": 199,
                    "volume": 750,
                    "productLaunchDate": "2020-01-01T00:00:00",
                    "isCompletelyOutOfStock": False,
                    "isTemporaryOutOfStock": False,
                },
                {
                    "productNumber": "1002",
                    "productNameBold": "Chianti",
                    "productNameThin": "Classico",
                    "country": "Italien",
                    "categoryLevel2": "Rött vin",
                    "categoryLevel3": "Druvigt & Mineraliskt",
                    "assortmentText": "Tillfälligt sortiment",
                    "alcoholPercentage": 12.5,
                    "vintage": "2020",
                    "price": 129,
                    "volume": 750,
                    "isCompletelyOutOfStock": True,
                    "isTemporaryOutOfStock": False,
                },
                {
                    "productNumber": "1003",
                    "productNameBold": "Magnum",
                    "country": "Italien",
                    "categoryLevel2": "Vitt vin",
                    "categoryLevel3": "Friskt & Fruktigt",
                    "assortmentText": "Fast sortiment",
                    "alcoholPercentage": 11.0,
                    "price": 350,
                    "volume": 1500,
                    "isCompletelyOutOfStock": False,
                    "isTemporaryOutOfStock": True,
                },
            ]
        ),
        encoding="utf-8",
    )

    (tmp_path / "0002.json").write_text(
        json.dumps(
            [
                {
                    "productNumber": "1001",  # duplicate of store 0001
                    "country": "Frankrike",
                    "categoryLevel2": "Rött vin",
                    "price": 199,
                    "volume": 750,
                },
                {
                    "productNumber": "2001",
                    "country": "Spanien",
                    "categoryLevel2": "Mousserande",
                    "categoryLevel3": "Aromatiskt",
                    "assortmentText": "Fast sortiment",
                    "alcoholPercentage": 11.5,
                    "price": 89,
                    "volume": 750,
                    "isCompletelyOutOfStock": False,
                    "isTemporaryOutOfStock": False,
                },
            ]
        ),
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture
def service(tmp_assortments: Path) -> AssortmentService:
    return AssortmentService(tmp_assortments)
