"""Tests for prompt construction (no network calls)."""
from __future__ import annotations

from app.services.ollama import (
    SYSTEM_PROMPT,
    build_user_message,
    number_wines_for_prompt,
)


def test_number_wines_assigns_sequential_ids() -> None:
    wines = [
        {"productNumber": "1001", "productNameBold": "A"},
        {"productNumber": "1002", "productNameBold": "B"},
        {"productNumber": "1003", "productNameBold": "C"},
    ]
    numbered = number_wines_for_prompt(wines)
    assert [w["id"] for w in numbered] == [1, 2, 3]
    assert numbered[0]["productNameBold"] == "A"


def test_number_wines_omits_empty_fields() -> None:
    wines = [{"productNumber": "1001", "productNameBold": "A", "vintage": None}]
    numbered = number_wines_for_prompt(wines)
    assert "vintage" not in numbered[0]


def test_number_wines_does_not_leak_product_number() -> None:
    """The 7-digit productNumber is intentionally not sent to the LLM."""
    wines = [{"productNumber": "1234567", "productNameBold": "A"}]
    numbered = number_wines_for_prompt(wines)
    assert "productNumber" not in numbered[0]


def test_build_user_message_contains_wines_and_user_request() -> None:
    numbered = [
        {"id": 1, "productNameBold": "Bordeaux", "vintage": "2018"}
    ]
    msg = build_user_message(numbered, "Pasta bolognese")
    assert "Pasta bolognese" in msg
    assert "Bordeaux" in msg
    assert '"id": 1' in msg


def test_build_user_message_handles_unicode() -> None:
    numbered = [{"id": 1, "country": "Österrike"}]
    msg = build_user_message(numbered, "vad rekommenderar du?")
    assert "Österrike" in msg


def test_system_prompt_describes_json_schema() -> None:
    assert "intro" in SYSTEM_PROMPT
    assert "picks" in SYSTEM_PROMPT
    assert '"id"' in SYSTEM_PROMPT
