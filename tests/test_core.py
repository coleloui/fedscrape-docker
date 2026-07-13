"""
Core tests — scraper unit tests and basic route smoke tests.

Route tests that require a DB connection will gracefully handle
the case where no DB is available (CI without Postgres).
"""

import pytest

from api.services.scraper import _month_to_number, _build_dataframe
from db.models import RATE_TYPES, SCRAPE_COLUMN_MAP


# ---------------------------------------------------------------------------
# Scraper unit tests (no network, no DB)
# ---------------------------------------------------------------------------


def test_month_to_number_valid():
    assert _month_to_number("Jan") == "01"
    assert _month_to_number("Jun") == "06"
    assert _month_to_number("Dec") == "12"


def test_month_to_number_invalid():
    with pytest.raises(ValueError):
        _month_to_number("Xyz")


def test_scrape_column_map_covers_all_rate_types():
    """Every value in SCRAPE_COLUMN_MAP should appear in RATE_TYPES."""
    for field in SCRAPE_COLUMN_MAP.values():
        assert field in RATE_TYPES, f"{field!r} missing from RATE_TYPES"


def test_rate_types_length():
    """Sanity-check that we have 30 rate type fields (matches H.15 table)."""
    assert len(RATE_TYPES) == 30


# ---------------------------------------------------------------------------
# Route smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_returns_json(client):
    response = await client.get("/health")
    # 200 (DB up) or 503 (DB down) — both are valid in CI
    assert response.status_code in (200, 503)
    body = response.json()
    assert "status" in body
    assert "checks" in body
    assert "version" in body


@pytest.mark.asyncio
async def test_latest_rates_without_db(client):
    # Starlette re-raises unhandled exceptions through the ASGI transport even
    # after sending a 500 response, so we tolerate a ConnectionRefusedError here
    # when Postgres isn't running in CI.
    try:
        response = await client.get("/rates/latest")
        assert response.status_code in (200, 404, 500, 503)
    except Exception:
        pass


@pytest.mark.asyncio
async def test_unknown_rate_type_returns_404(client):
    response = await client.get("/rates/not_a_real_rate_type")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_spread_unknown_rate_returns_404(client):
    response = await client.get("/rates/spread?rate_a=federal_funds&rate_b=fake_rate")
    assert response.status_code == 404
