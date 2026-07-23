"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.config import settings
from api.limiter import limiter
from api.routes import chat, health, rates
from db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API listening internally on port %s", settings.PORT)
    # TODO: Replace create_all() with Alembic before first schema
    # change post-launch. Add Railway release command: alembic upgrade head
    await init_db()
    yield


app = FastAPI(
    title="FedScrape API",
    description="Federal Reserve H.15 interest rate data.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(rates.router)
app.include_router(chat.router)
