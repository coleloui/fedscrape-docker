# FedScrape — Infrastructure & GenAI Buildout

## Who you are and what exists

You are working inside the `fedscrape-docker` repository. The existing structure is:

```
fedscrape-docker/
├── api/
│   ├── main.py              # FastAPI app — lifespan, CORS, routers
│   ├── config.py            # pydantic-settings — Settings class
│   ├── routes/
│   │   ├── rates.py         # all rate endpoints
│   │   └── health.py        # GET /health
│   ├── services/
│   │   ├── scraper.py       # Fed H.15 scrape logic
│   │   └── run_scrape.py    # standalone cron entrypoint
│   └── models/
│       └── rate.py          # Pydantic response schemas
├── db/
│   ├── models.py            # SQLModel RateRecord table + RATE_COLUMNS dict
│   ├── crud.py              # async query helpers
│   └── session.py           # async engine + get_session dependency
├── mcp/
│   └── server.py            # MCP server with 6 rate tools
├── tests/
│   └── test_core.py
├── docker-compose.yml       # db, api, scraper (cron), mcp services
├── Dockerfile
├── requirements.txt
└── .env.example
```

Read every file listed above before writing any code. Use the existing
patterns — async SQLModel sessions, pydantic-settings config, FastAPI
dependency injection — don't introduce new patterns that conflict.

---

## Phase 1 — Railway deployment configuration

### What Railway needs

Railway deploys each service in docker-compose as a separate Railway service.
It injects `DATABASE_URL` and `REDIS_URL` automatically when you attach those
plugins. We need config files that tell Railway how to build and run each service.

### Tasks

**1. Create `railway.toml` at the repo root**

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**2. Create `railway/` directory with per-service configs**

Railway uses a `railway.json` or service-level config for multi-service repos.
Create `railway/api.json`, `railway/scraper.json`, `railway/mcp.json` that
specify the start command for each service:

- api: `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`
  (Railway injects $PORT automatically — do not hardcode 8000)
- scraper: `python -m api.services.run_scrape`
  (Railway cron — set schedule to `0 18 * * 1-5` in the Railway dashboard,
   document this in DEPLOYMENT.md)
- mcp: `python mcp/server.py`

**3. Update `Dockerfile`**

Current Dockerfile hardcodes `EXPOSE 8000`. Railway uses `$PORT` env var.
Update the CMD to use `$PORT`:

```dockerfile
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**4. Update `api/config.py`**

Add `REDIS_URL` to Settings:

```python
REDIS_URL: str = "redis://localhost:6379"
PORT: int = 8000  # Railway overrides this via $PORT
```

**5. Update `.env.example`**

Add:
```
REDIS_URL=redis://localhost:6379
PORT=8000
```

**6. Create `DEPLOYMENT.md`**

Document the full Railway setup process:
- Create a new Railway project
- Add a GitHub repo source
- Add a Postgres plugin → DATABASE_URL is auto-injected
- Add a Redis plugin → REDIS_URL is auto-injected
- Create three services: api, scraper, mcp
- Set the scraper service to a cron schedule: `0 18 * * 1-5`
- Required environment variables per service (ADMIN_API_KEY, SECRET_KEY, etc.)
- How to trigger a manual scrape: Railway "Run Now" on the scraper service
- Custom domain setup

---

## Phase 2 — GitHub Actions CI/CD

### What we want

On every push to `main`:
1. Run the test suite
2. If tests pass, trigger a Railway redeploy via Railway's deploy hook

On pull requests:
1. Run the test suite only (no deploy)

### Tasks

**1. Create `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: fedscrape
          POSTGRES_PASSWORD: fedscrape
          POSTGRES_DB: fedscrape
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://fedscrape:fedscrape@localhost:5432/fedscrape
          REDIS_URL: redis://localhost:6379
          APP_ENV: test
          ADMIN_API_KEY: test-admin-key
          SECRET_KEY: test-secret
        run: pytest tests/ -v --tb=short
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Trigger Railway deploy
        run: |
          curl -X POST "${{ secrets.RAILWAY_DEPLOY_WEBHOOK }}"
```

**2. Document required GitHub secrets in `DEPLOYMENT.md`**

Add a section listing:
- `RAILWAY_DEPLOY_WEBHOOK` — get from Railway service settings → Deploy Webhooks

**3. Update `tests/conftest.py`**

Write a proper async test client fixture using `httpx.AsyncClient` and
`ASGITransport`. Use a test Postgres DB (from the CI service above).
The fixture should call `init_db()` on setup and drop all tables on teardown.

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel

from api.main import app
from db.session import engine, init_db

@pytest_asyncio.fixture
async def async_client():
    await init_db()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

---

## Phase 3 — Redis caching and rate limiting

### Caching strategy

- Cache `GET /rates/latest` → key `rates:latest`, TTL 1 hour
- Cache `GET /rates/{rate_type}` series responses → key `rates:series:{rate_type}:{start}:{end}:{limit}`, TTL 1 hour
- Cache `GET /rates/spread` → key `rates:spread:{a}:{b}:{date}`, TTL 1 hour
- Do NOT cache `POST /rates/refresh` (it's a write operation)
- Cache is invalidated on successful `POST /rates/refresh`

### Rate limiting strategy

Use `slowapi` with Redis as the backend:
- Unauthenticated requests: 60 requests/minute per IP
- Admin endpoints (`POST /rates/refresh`): 5 requests/minute per IP

### Tasks

**1. Add to `requirements.txt`**

```
redis[asyncio]==5.0.8
slowapi==0.1.9
```

**2. Create `api/cache.py`**

```python
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
```

**3. Update `api/routes/rates.py`**

Wrap the three cacheable endpoints with cache_get/cache_set calls:

- Before hitting the DB, check the cache
- On cache hit, return the cached value directly (skip DB entirely)
- On cache miss, query DB, store result in cache, return result
- On `POST /rates/refresh` success, call `cache_delete_pattern("rates:*")`

The cache key for series should include all query params so different date
ranges don't collide: `f"rates:series:{rate_type}:{start}:{end}:{limit}"`

**4. Create `api/limiter.py`**

```python
"""slowapi rate limiter wired to Redis."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from api.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
)
```

**5. Update `api/main.py`**

Register the limiter with the FastAPI app:

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api.limiter import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**6. Apply rate limit decorators in `api/routes/rates.py`**

```python
from api.limiter import limiter

@router.get("/latest")
@limiter.limit("60/minute")
async def get_latest_rates(request: Request, ...):
    ...

@router.post("/refresh")
@limiter.limit("5/minute")
async def trigger_refresh(request: Request, ...):
    ...
```

---

## Phase 4 — Chat endpoint (Anthropic API + MCP tools in loop)

### What this builds

A stateless chat endpoint that accepts a conversation history and a user
message, calls Claude Sonnet with your rate tools available, and streams
the response back. The frontend will maintain conversation state client-side
and send the full history on each request.

### Tasks

**1. Add to `requirements.txt`**

```
anthropic==0.34.2
```

**2. Add to `api/config.py`**

```python
ANTHROPIC_API_KEY: str = ""
ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
```

**3. Add to `.env.example`**

```
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-6
```

**4. Create `api/services/chat.py`**

This service wraps the Anthropic API. It:
- Accepts a list of message dicts (role/content) representing conversation history
- Defines the rate tools as Anthropic tool definitions (mirroring what's in mcp/server.py)
- Executes tool calls by hitting your own FastAPI endpoints internally
  (use httpx to call `http://localhost:{settings.PORT}/rates/...`)
- Handles the tool use → tool result → final response loop
- Returns the assistant's final text response

The tools to define (matching mcp/server.py exactly):
- `list_rate_types`
- `get_latest_rates` (with optional `fields` array param)
- `get_rate_series` (rate_type, start, end, limit)
- `get_rate_average` (rate_type, start, end)
- `get_yield_spread` (rate_a, rate_b, date optional)

System prompt for the chat service:

```
You are a Federal Reserve interest rate analyst with access to real-time 
H.15 rate data. You can answer questions about current rates, historical 
trends, yield curve analysis, and rate comparisons across any time period.

When answering:
- Always fetch current data before making claims about specific values
- Format rate values as percentages to 2 decimal places (e.g. 5.33%)
- When discussing yield curve shape, always check the 10y-2y spread
- Be concise and data-forward — lead with the numbers, follow with context
- If asked about future rates, be clear you can only provide historical data

Available data: Federal Reserve H.15 release — daily rates from the Fed 
including Fed Funds, Treasury bills, Treasury notes/bonds (nominal and TIPS), 
commercial paper, and bank prime loan rate.
```

**5. Create `api/routes/chat.py`**

```python
"""Chat endpoint — conversational interface over rate data."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal

from api.limiter import limiter
from api.services.chat import run_chat

router = APIRouter(prefix="/chat", tags=["chat"])


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]  # full conversation history, last message is the new user turn


class ChatResponse(BaseModel):
    message: str             # assistant's response text
    tool_calls_made: int     # how many tool calls were used to answer


@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Send a message and receive a data-backed response from Claude.
    
    The client is responsible for maintaining conversation history and 
    sending the full messages array on each request. The last message
    must have role='user'.
    """
    if not body.messages or body.messages[-1].role != "user":
        raise HTTPException(status_code=422, detail="Last message must be role='user'")
    
    if len(body.messages) > 20:
        raise HTTPException(status_code=422, detail="Maximum 20 messages per request")
    
    result = await run_chat([m.model_dump() for m in body.messages])
    return ChatResponse(**result)
```

**6. Register the chat router in `api/main.py`**

```python
from api.routes import health, rates, chat
app.include_router(chat.router)
```

---

## After all phases — validation checklist

Run through these manually before considering the work done:

**Railway config**
- [ ] `railway.toml` exists at repo root
- [ ] Dockerfile CMD uses `${PORT:-8000}`
- [ ] `DEPLOYMENT.md` documents every manual Railway step

**CI/CD**
- [ ] `.github/workflows/ci.yml` exists
- [ ] `tests/conftest.py` has the async_client fixture
- [ ] All existing tests in `test_core.py` pass locally with `pytest tests/ -v`

**Redis**
- [ ] `api/cache.py` exists with get/set/delete_pattern
- [ ] `/rates/latest` returns a cached response on second call (verify with Redis CLI: `redis-cli keys "rates:*"`)
- [ ] `POST /rates/refresh` clears the cache
- [ ] Rate limiting returns 429 after limit is exceeded

**Chat**
- [ ] `POST /chat` with `{"messages": [{"role": "user", "content": "What is the current Fed Funds rate?"}]}` returns a response with actual rate data in it
- [ ] Tool calls are logged (add `logger.info("Tool call: %s", tool_name)` in chat.py)
- [ ] Multi-turn conversation works (send 2-message history, get coherent follow-up)

---

## Notes for Claude Code

- Do not add any packages not listed in the tasks above
- Do not change the DB schema in `db/models.py` — it is already correct
- Do not change the MCP server in `mcp/server.py` — it is separate from the chat service
- The chat service calls the API internally via httpx, it does NOT import from db/ directly
- All new config values go in `api/config.py` Settings class and `.env.example`
- Keep `run_scrape.py` unchanged — it is called by Railway cron as-is
- If a task says "document in DEPLOYMENT.md", add a section there, don't just add a comment
