"""Health check — validates DB connectivity and returns 503 on failure."""

import logging

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health(
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """
    Health check endpoint.

    Returns 200 when all dependencies are reachable.
    Returns 503 when any dependency is down.

    Used by Railway and Docker Compose for deploy health-gating.
    """
    checks: dict[str, str] = {}
    healthy = True

    try:
        await session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as exc:
        logger.error("Health check — DB unreachable: %s", exc)
        checks["db"] = f"error: {exc}"
        healthy = False

    # Redis check placeholder (wire in when Redis is added):
    # try:
    #     await redis.ping()
    #     checks["redis"] = "ok"
    # except Exception as exc:
    #     checks["redis"] = f"error: {exc}"
    #     healthy = False

    if not healthy:
        response.status_code = 503

    return {
        "status": "ok" if healthy else "degraded",
        "checks": checks,
        "version": "1.0.0",
    }
