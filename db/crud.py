import datetime
from typing import Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import desc, select

from db.models import RATE_TYPES, RateRecord


async def upsert_record(session: AsyncSession, record: RateRecord) -> None:
    """Insert or update a single RateRecord, keyed on date."""
    values = record.model_dump(exclude={"id"})
    stmt = pg_insert(RateRecord).values(**values)
    update_cols = {k: stmt.excluded[k] for k in values if k != "date"}
    stmt = stmt.on_conflict_do_update(index_elements=["date"], set_=update_cols)
    await session.execute(stmt)
    await session.commit()


async def upsert_records(session: AsyncSession, records: list[RateRecord]) -> int:
    """Upsert a batch of records. Returns the count upserted."""
    for record in records:
        await upsert_record(session, record)
    return len(records)


async def get_latest(session: AsyncSession) -> Optional[RateRecord]:
    result = await session.execute(
        select(RateRecord).order_by(desc(RateRecord.date)).limit(1)
    )
    return result.scalar_one_or_none()


async def get_by_date(session: AsyncSession, d: datetime.date) -> Optional[RateRecord]:
    result = await session.execute(
        select(RateRecord).where(RateRecord.date == d)
    )
    return result.scalar_one_or_none()


async def get_series(
    session: AsyncSession, rate_type: str, limit: int = 30
) -> list[dict]:
    """Return the most recent `limit` (date, value) pairs for one rate type."""
    col = getattr(RateRecord, rate_type)
    result = await session.execute(
        select(RateRecord.date, col).order_by(desc(RateRecord.date)).limit(limit)
    )
    return [{"date": row[0], "value": row[1]} for row in result.all()]


async def get_average(
    session: AsyncSession, rate_type: str, days: int = 30
) -> Optional[float]:
    """Return the mean of the most recent `days` non-null values for a rate type."""
    col = getattr(RateRecord, rate_type)
    result = await session.execute(
        select(col)
        .where(col.isnot(None))
        .where(col != "n.a.")
        .order_by(desc(RateRecord.date))
        .limit(days)
    )
    values: list[float] = []
    for (v,) in result.all():
        try:
            values.append(float(v))
        except (TypeError, ValueError):
            pass
    return sum(values) / len(values) if values else None
