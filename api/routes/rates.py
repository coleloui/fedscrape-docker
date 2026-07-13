"""Rate data endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

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
async def latest_rates(session: AsyncSession = Depends(get_session)):
    """Return the most recent H.15 rate record."""
    record = await get_latest(session)
    if record is None:
        raise HTTPException(status_code=404, detail="No rate data in database.")
    return record


@router.get("/spread", response_model=SpreadResponse)
async def yield_spread(
    rate_a: str = Query(..., description="First rate-type slug"),
    rate_b: str = Query(..., description="Second rate-type slug"),
    session: AsyncSession = Depends(get_session),
):
    """Compute the spread (rate_a − rate_b) from the latest record."""
    for slug in (rate_a, rate_b):
        if slug not in RATE_TYPES:
            raise HTTPException(status_code=404, detail=f"Unknown rate type: {slug!r}")

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

    return SpreadResponse(date=record.date, rate_a=rate_a, rate_b=rate_b, spread=spread)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_rates(session: AsyncSession = Depends(get_session)):
    """Scrape the latest Fed H.15 data and upsert into the database."""
    try:
        records = scrape_latest()
    except Exception as exc:
        logger.exception("Scrape failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Scrape failed: {exc}")

    count = await upsert_records(session, records)
    return RefreshResponse(upserted=count)


@router.get("/{rate_type}", response_model=RateSeriesResponse)
async def rate_series(
    rate_type: str,
    limit: int = Query(30, ge=1, le=365, description="Number of recent records to return"),
    session: AsyncSession = Depends(get_session),
):
    """Return a time series for a single rate type."""
    if rate_type not in RATE_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown rate type: {rate_type!r}")

    rows = await get_series(session, rate_type, limit)
    return RateSeriesResponse(
        rate_type=rate_type,
        data=[RateSeriesEntry(date=r["date"], value=r["value"]) for r in rows],
    )
