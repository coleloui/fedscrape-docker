"""slowapi rate limiter wired to Redis."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from api.config import settings


def _get_key(request):
    if settings.APP_ENV == "test":
        return "test-bypass"
    return get_remote_address(request)


limiter = Limiter(
    key_func=_get_key,
    enabled=settings.APP_ENV != "test",
    storage_uri=settings.REDIS_URL if settings.APP_ENV != "test" else "memory://",
)
