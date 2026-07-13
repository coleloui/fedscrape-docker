"""Redis cache client and helpers."""

import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from api.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Optional[Any]:
    """Return parsed JSON value for key, or None on miss/error."""
    try:
        r = await get_redis()
        val = await r.get(key)
        return json.loads(val) if val else None
    except Exception as exc:
        logger.warning("Cache GET failed for %s: %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Serialize value to JSON and store with TTL. Fails silently."""
    try:
        r = await get_redis()
        await r.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as exc:
        logger.warning("Cache SET failed for %s: %s", key, exc)


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a pattern. Used for cache invalidation."""
    try:
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
    except Exception as exc:
        logger.warning("Cache DELETE failed for pattern %s: %s", pattern, exc)
