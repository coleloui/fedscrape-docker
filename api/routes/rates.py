"""Rate data endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.cache import cache_delete_pattern, cache_get, cache_set
from api.limiter import limiter
from api.models.rate import (
    RateResponse,
    RateSeriesEntry,
    RateSeriesResponse,
    RefreshResponse,
    SpreadResponse,
)
from api.services.scraper import scrape_latest
from db.crud import get_average, get_by_date, get_latest, get_series, upsert_records
from db.models import RATE_TYPES
from db.session import get_session

router = APIRouter(prefix="/rates", tags=["rates"])
logger = logging.getLogger(__name__)


@router.get("/latest", response_model=RateResponse)
@limiter.limit("60/minute")
async def latest_rates(request: Request, session: AsyncSession = Depends(get_session)):
    """Return the most recent H.15 rate record."""
    cached = await cache_get("rates:latest")
    if cached is not None:
        return cached

    record = await get_latest(session)
    if record is None:
        raise HTTPException(status_code=404, detail="No rate data in database.")

    result = RateResponse.model_validate(record).model_dump(mode="json")
    await cache_set("rates:latest", result)
    return result


@router.get("/spread", response_model=SpreadResponse)
@limiter.limit("60/minute")
async def yield_spread(
    request: Request,
    rate_a: str = Query(..., description="First rate-type slug"),
    rate_b: str = Query(..., description="Second rate-type slug"),
    session: AsyncSession = Depends(get_session),
):
    """Compute the spread (rate_a − rate_b) from the latest record."""
    for slug in (rate_a, rate_b):
        if slug not in RATE_TYPES:
            raise HTTPException(status_code=404, detail=f"Unknown rate type: {slug!r}")

    cache_key = f"rates:spread:{rate_a}:{rate_b}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    record = await get_latest(session)
    if record is None:
        raise HTTPException(status_code=404, detail="No rate data in database.")

    val_a = getattr(record, rate_a)
    val_b = getattr(record, rate_b)
    try:
        spread = float(val_a) - float(val_b)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail="Cannot compute spread — one or both rates are unavailable (n.a.).",
        )

    result = SpreadResponse(date=record.date, rate_a=rate_a, rate_b=rate_b, spread=spread)
    await cache_set(cache_key, result.model_dump(mode="json"))
    return result


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("5/minute")
async def refresh_rates(request: Request, session: AsyncSession = Depends(get_session)):
    """Scrape the latest Fed H.15 data and upsert into the database."""
    try:
        records = scrape_latest()
    except Exception as exc:
        logger.exception("Scrape failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Scrape failed: {exc}")

    count = await upsert_records(session, records)
    await cache_delete_pattern("rates:*")
    return RefreshResponse(upserted=count)


def slug_to_display(slug: str) -> str:
    """Convert a rate-type slug to a human-readable label, e.g. treasury_10y -> Treasury 10Y."""
    return " ".join(
        part.upper() if len(part) <= 2 else part.capitalize() for part in slug.split("_")
    )


@router.get("/types")
async def list_rate_types():
    """Return all known rate-type slugs mapped to human-readable display names."""
    return {"rate_types": {slug: slug_to_display(slug) for slug in RATE_TYPES}}


@router.get("/{rate_type}/average")
@limiter.limit("60/minute")
async def rate_average(
    request: Request,
    rate_type: str,
    days: int = Query(30, ge=1, le=3650, description="Trailing window size in days"),
    session: AsyncSession = Depends(get_session),
):
    """Return the mean of the most recent `days` non-null values for a rate type."""
    if rate_type not in RATE_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown rate type: {rate_type!r}")

    average = await get_average(session, rate_type, days=days)
    return {
        "rate_type": rate_type,
        "display_name": slug_to_display(rate_type),
        "days": days,
        "average": average,
    }


@router.get("/{rate_type}", response_model=RateSeriesResponse)
@limiter.limit("60/minute")
async def rate_series(
    request: Request,
    rate_type: str,
    limit: int = Query(30, ge=1, le=365, description="Number of recent records to return"),
    session: AsyncSession = Depends(get_session),
):
    """Return a time series for a single rate type."""
    if rate_type not in RATE_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown rate type: {rate_type!r}")

    cache_key = f"rates:series:{rate_type}:{limit}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    rows = await get_series(session, rate_type, limit)
    result = RateSeriesResponse(
        rate_type=rate_type,
        data=[RateSeriesEntry(date=r["date"], value=r["value"]) for r in rows],
    )
    data = result.model_dump(mode="json")
    await cache_set(cache_key, data)
    return data
