# Project Architecture

## Directory Structure

```
fedscrape-docker/
├── api/                    # FastAPI application
│   ├── main.py             # FastAPI app factory + lifespan
│   ├── config.py           # Settings (pydantic-settings)
│   ├── cache.py            # Redis caching helpers
│   ├── limiter.py          # slowapi rate limiter
│   ├── models/             # Pydantic response models
│   │   └── rate.py
│   ├── routes/              # FastAPI route handlers
│   │   ├── health.py
│   │   ├── rates.py
│   │   └── chat.py
│   └── services/            # Business logic layer
│       ├── scraper.py        # H.15 HTML scraping
│       ├── chat.py            # Claude tool-use loop
│       ├── downloader.py       # bulk CSV download of H.15 series (parallel, requests)
│       └── upload.py            # S3 upload gating
├── db/                     # Database layer
│   ├── session.py           # engine, AsyncSessionLocal, get_session, init_db
│   ├── models.py             # RateRecord (SQLModel), RATE_TYPES, SCRAPE_COLUMN_MAP
│   └── crud.py                # async query/upsert functions
│   # No alembic/ directory — schema is created via
│   # SQLModel.metadata.create_all() on startup, not migrations.
│   # See database.md for why, and the TODO in api/main.py.
├── fedscrape/              # Core scraping logic and CLI
│   ├── cli.py                # Typer CLI entrypoint
│   └── mcp_server.py           # MCP server implementation
├── fedscrape-ui/           # Frontend (Vite + React + TS) — see frontend.md
│   └── src/
│       ├── api/               # generated typed client + config.ts
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       └── lib/
├── tests/                  # Test suite
│   ├── conftest.py           # client / async_client fixtures
│   └── test_core.py            # scraper unit tests + route smoke tests
├── .claude/                # Claude Code instructions (this directory)
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # Application container
├── pyproject.toml          # Python project config, ruff config
├── package.json            # repo-root husky/lint-staged config only
└── README.md               # Project documentation
```

## Architectural Patterns

### Layered Architecture

The project follows a clean layered architecture:

1. **API Layer** (`api/`)
   - FastAPI routes and request/response models
   - Input validation with Pydantic
   - Dependency injection for services
   - Error handling and HTTP responses

2. **Service Layer** (`api/services/`)
   - Business logic and orchestration
   - Interacts with database layer
   - Handles caching logic
   - No direct HTTP concerns

3. **Database Layer** (`db/`)
   - SQLModel models (combines SQLAlchemy + Pydantic)
   - Database session management
   - Query logic
   - No migration framework yet — see [database.md](database.md)

4. **Core Logic** (`fedscrape/`)
   - Domain-specific logic (web scraping)
   - CLI commands
   - MCP server

5. **Frontend** (`fedscrape-ui/`)
   - Standalone Vite + React app, independent of the Python layers above
   - Consumes the API layer exclusively through a generated typed client
     (see [api-generation.md](api-generation.md)) — never hand-written
     fetch calls
   - See [frontend.md](frontend.md) for structure and conventions
   - Independent of API layer

### Key Patterns

These describe what the code actually does, not hypothetical alternatives.
See [backend.md](backend.md) and [database.md](database.md) for more detail
on each.

#### Route handlers call the DB layer directly — no service classes

There is no `RateService`/`RateRepository` class hierarchy. Route handlers
in `api/routes/*.py` call plain async functions in `db/crud.py` directly,
passing an `AsyncSession` obtained via FastAPI's `Depends(get_session)`:

```python
@router.get("/{rate_type}/average", response_model=RateAverageResponse)
@limiter.limit("60/minute")
async def rate_average(
    request: Request,
    rate_type: str,
    days: int = Query(30, ge=1, le=3650),
    session: AsyncSession = Depends(get_session),
):
    if rate_type not in RATE_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown rate type: {rate_type!r}")
    average = await get_average(session, rate_type, days=days)
    return {"rate_type": rate_type, "days": days, "average": average}
```

`api/services/` holds logic that's more than "call one CRUD function" —
the H.15 scraper, the chat tool-use loop, S3 upload gating — but even
these call `db/crud.py` functions directly rather than going through an
intermediate service/repository object. `api/services/chat.py`'s tools
open their own `AsyncSessionLocal()` context per call:

```python
async def _execute_tool(name: str, tool_input: dict) -> str:
    if name == "get_rate_average":
        rate_type = tool_input["rate_type"]
        days = tool_input.get("days", 30)
        async with AsyncSessionLocal() as session:
            avg = await get_average(session, rate_type, days)
        return json.dumps({"rate_type": rate_type, "days": days, "average": avg})
```

This replaced an earlier version that called the API's own HTTP routes
over `httpx` (self-calls to `localhost`) — that broke on Railway, since a
service can't reliably call its own public URL, and needed manual
`INTERNAL_API_URL` port tracking. Direct DB access is the standing
pattern now; don't reintroduce an HTTP round-trip from inside this same
process.

#### The rate model (`db/models.py`)

The one table is `RateRecord` (`__tablename__ = "rate_records"`) — not
`InterestRate`. `id` + `date` (unique, indexed) + ~29 `Optional[str]`
columns, one per Fed H.15 series (`federal_funds`, `treasury_10y`,
`tbill_3m`, ...). Every rate value is a string, not a float — the
scraper stores the Fed's raw text verbatim, including the literal
`"n.a."` for unavailable data. See [database.md](database.md) for the
full column list and the `RATE_TYPES`/`SCRAPE_COLUMN_MAP` helpers.

#### Configuration (`api/config.py`)

One `Settings(BaseSettings)` class, instantiated once as the
module-level `settings` singleton — imported wherever needed
(`from api.config import settings`), never re-instantiated. Field names
are `UPPER_CASE` matching the env vars directly (`DATABASE_URL`,
`REDIS_URL`, `ANTHROPIC_API_KEY`, ...), not the `snake_case`-with-alias
pattern some Pydantic Settings examples use. All fields have sane local
defaults so the app boots without a `.env` file present (important for
CI, where env vars are injected directly).

#### Caching (`api/cache.py`)

No decorator-based caching layer — no `@cache.cached(...)`. Three plain
async functions instead: `cache_get(key)`, `cache_set(key, value, ttl=3600)`,
`cache_delete_pattern(pattern)`. Each one catches its own exceptions and
logs a warning rather than propagating, so a Redis outage degrades
gracefully to "always miss" rather than 500ing every request. Called
directly inside route handlers, not via a decorator:

```python
cached = await cache_get("rates:latest")
if cached is not None:
    return cached
...
await cache_set("rates:latest", result)
```

#### Rate limiting (`api/limiter.py`)

`slowapi.Limiter` keyed on remote IP, backed by the same Redis instance
as the cache. Applied per-route via `@limiter.limit("60/minute")` —
every decorated route must also accept `request: Request` as its first
parameter. Disabled entirely when `Settings.APP_ENV == "test"`.

#### CLI (`fedscrape/cli.py`)

Typer app with three commands: `fedscrape serve` (runs the FastAPI app
via uvicorn), `fedscrape scrape` (runs one scrape-and-upsert pass,
supports `--dry-run`), `fedscrape mcp-serve` (starts the MCP server over
stdio). This is the single entrypoint for all three Railway services —
see [DEPLOYMENT.md](../DEPLOYMENT.md) for how each is configured.

#### MCP server (`fedscrape/mcp_server.py`)

Exposes the same rate-lookup capabilities as the REST API and the chat
tool-use loop, but over the Model Context Protocol (`list_tools()` /
`call_tool()`) for use by MCP-compatible LLM clients, independent of the
`/chat` endpoint.

## Planned / not-yet-done

These are known future directions, not current behavior — don't assume
any of this exists yet:

- **Database migrations (Alembic)**: deliberately not set up yet. See
  [database.md](database.md) for the reasoning and the `TODO` marker in
  `api/main.py`. Don't add this without being asked — it's been tried
  once and reverted.
- **Pyright in strict mode, enforced pre-commit**: Pyright is available
  to run manually but isn't wired into CI or the commit hook. See
  [git-hooks.md](git-hooks.md).
- **Frontend automated tests**: no Vitest/Playwright suite exists for
  `fedscrape-ui` yet (see [testing.md](testing.md)).
- **Monorepo/package split**: the codebase is a single Python package
  plus a standalone frontend, not a `packages/`+`services/` monorepo.
  There's no current plan to split it up — this codebase is small enough
  that the layered structure described above is sufficient.
