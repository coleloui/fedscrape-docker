# FedScrape — Application Cleanup (Pre-Infra)

## Goal

Before any deployment or infrastructure work, this codebase needs to be a
properly structured, installable Python package with real CLI entrypoints,
clean imports, and a health check that actually validates dependencies.

Do NOT add any new features. Do NOT touch business logic in scraper.py,
crud.py, or the rate routes. This is purely structural cleanup.

---

## Current problems to fix

1. `run_scrape.py` is a script with `if __name__ == "__main__"` and `sys.exit()`
   — not invokable as a proper CLI command
2. No `pyproject.toml` — the package isn't installable, entrypoints aren't defined,
   imports rely on CWD luck
3. `mcp/server.py` hardcodes `API_BASE = f"http://localhost:{settings.API_PORT}"`
   — breaks in any multi-container environment
4. `health.py` returns `{"status": "ok"}` with a dummy DB check — not useful
   for Railway's health check system
5. `requirements.txt` mixes prod and dev deps with no separation
6. No `__init__.py` files are verified to exist at every package level

---

## Step 1 — Audit the existing structure

Before writing any code, read every file in the project:

```
api/__init__.py
api/main.py
api/config.py
api/models/__init__.py
api/models/rate.py
api/routes/__init__.py
api/routes/rates.py
api/routes/health.py
api/services/__init__.py
api/services/scraper.py
api/services/run_scrape.py
db/__init__.py
db/models.py
db/crud.py
db/session.py
mcp/__init__.py
mcp/server.py
tests/__init__.py
tests/conftest.py
tests/test_core.py
Dockerfile
docker-compose.yml
.env.example
requirements.txt
```

Confirm every `__init__.py` exists. If any are missing, create them as empty files.

---

## Step 2 — Create `pyproject.toml`

Replace `requirements.txt` as the canonical dependency definition.
Keep `requirements.txt` but have it contain only: `-e .` so pip installs
the package in editable mode, which makes imports work correctly everywhere.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "fedscrape"
version = "1.0.0"
description = "Federal Reserve H.15 interest rate data API and MCP server"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.30.6",
    "httpx==0.27.2",
    "sqlmodel==0.0.21",
    "asyncpg==0.29.0",
    "alembic==1.13.3",
    "requests==2.32.3",
    "beautifulsoup4==4.12.3",
    "pandas==2.2.3",
    "mcp==1.1.2",
    "boto3==1.35.36",
    "python-dotenv==1.0.1",
    "pydantic-settings==2.5.2",
    "typer==0.12.5",
    "rich==13.9.2",
]

[project.optional-dependencies]
dev = [
    "pytest==8.3.3",
    "pytest-asyncio==0.24.0",
    "httpx==0.27.2",
]

[project.scripts]
fedscrape = "fedscrape.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["fedscrape", "api", "db", "mcp"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.hatch.metadata]
allow-direct-references = true
```

---

## Step 3 — Create the CLI package

Create `fedscrape/` as a top-level package with a Typer-based CLI.
This is what gets exposed as the `fedscrape` command via `pyproject.toml`.

### `fedscrape/__init__.py`
Empty file.

### `fedscrape/cli.py`

```python
"""
FedScrape CLI — application entrypoints.

Usage:
    fedscrape serve       Start the API server
    fedscrape scrape      Run a single Fed H.15 scrape and upsert
    fedscrape mcp         Start the MCP server
"""

import asyncio
import logging
import sys

import typer
from rich.console import Console
from rich.logging import RichHandler

app = typer.Typer(
    name="fedscrape",
    help="Federal Reserve H.15 interest rate data — API, MCP server, and scraper.",
    no_args_is_help=True,
)
console = Console()


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, envvar="PORT", help="Bind port"),
    reload: bool = typer.Option(False, help="Enable auto-reload (development only)"),
    log_level: str = typer.Option("info", help="Uvicorn log level"),
) -> None:
    """Start the FedScrape API server."""
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


@app.command()
def scrape(
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse without writing to DB"),
) -> None:
    """
    Fetch the latest Fed H.15 release and upsert into the database.

    Exit codes:
        0 — success
        1 — scrape or DB error
    """
    _setup_logging()
    logger = logging.getLogger("fedscrape.scrape")

    async def _run() -> int:
        from api.services.scraper import scrape_latest
        from db.crud import upsert_record
        from db.session import AsyncSessionLocal, init_db

        logger.info("Starting Fed H.15 scrape...")

        try:
            records = scrape_latest()
        except Exception as exc:
            logger.exception("Scrape failed — could not fetch/parse Fed H.15: %s", exc)
            return 1

        if not records:
            logger.warning("Scrape returned 0 records.")
            return 1

        logger.info("Parsed %d records.", len(records))

        if dry_run:
            logger.info("Dry run — skipping DB upsert.")
            return 0

        try:
            await init_db()
            async with AsyncSessionLocal() as session:
                for record in records:
                    await upsert_record(session, record)
            logger.info("Upserted %d records.", len(records))
            return 0
        except Exception as exc:
            logger.exception("DB upsert failed: %s", exc)
            return 1

    exit_code = asyncio.run(_run())
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


@app.command()
def mcp_serve() -> None:
    """Start the FedScrape MCP server (stdio transport)."""
    _setup_logging()
    import asyncio
    from mcp.server_impl import run_mcp_server
    asyncio.run(run_mcp_server())
```

---

## Step 4 — Refactor `api/services/run_scrape.py`

This file is now redundant — its logic lives in `fedscrape/cli.py` under
the `scrape` command. Replace it with a thin shim that calls the CLI for
backwards compatibility with any existing docker-compose or cron references:

```python
"""
Backwards-compatible shim — prefer `fedscrape scrape` going forward.
This file exists so existing cron configs and docker-compose commands
continue to work without change during the migration period.
"""
import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run(["fedscrape", "scrape"] + sys.argv[1:])
    sys.exit(result.returncode)
```

Update `docker-compose.yml` scraper service command from:
```
python -m api.services.run_scrape
```
to:
```
fedscrape scrape
```

---

## Step 5 — Fix `mcp/server.py`

The hardcoded `API_BASE` must be replaced with a configurable env var.

**In `api/config.py`**, add:
```python
API_BASE_URL: str = "http://localhost:8000"
```

**In `.env.example`**, add:
```
# Internal URL the MCP server uses to reach the API
# In Docker: http://fedscrape_api:8000
# In Railway: set to the internal Railway service URL
API_BASE_URL=http://localhost:8000
```

**In `mcp/server.py`**, replace:
```python
API_BASE = f"http://localhost:{settings.API_PORT}"
```
with:
```python
from api.config import settings
API_BASE = settings.API_BASE_URL
```

**Also in `mcp/server.py`**: extract the `main()` function into
`mcp/server_impl.py` as `run_mcp_server()` so the CLI can import it
without running it:

Create `mcp/server_impl.py`:
```python
"""Importable MCP server runner — called by fedscrape mcp CLI command."""

from mcp.server.stdio import stdio_server
# import the app object from server.py (not the __main__ block)
from mcp.server import app  # the Server instance


async def run_mcp_server() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
```

Update `mcp/server.py` to remove the `if __name__ == "__main__"` block
(the CLI handles that now) and import `run_mcp_server` is available
from `mcp/server_impl.py`.

---

## Step 6 — Improve `api/routes/health.py`

The current health check is a stub. Replace it with one that validates
all critical dependencies — DB connectivity and (once Redis is added)
Redis connectivity. Railway uses this endpoint to determine if a deploy
succeeded, so it must actually reflect real application health.

```python
"""Health check — validates DB (and Redis when configured)."""

import logging
from fastapi import APIRouter, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.session import get_session
from api.config import settings

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health(
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """
    Health check endpoint.

    Returns 200 if all dependencies are reachable.
    Returns 503 if any dependency is down.

    Used by Railway for deploy health gating and zero-downtime deploys.
    """
    checks: dict[str, str] = {}
    healthy = True

    # Database check
    try:
        await session.exec(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as exc:
        logger.error("Health check — DB unreachable: %s", exc)
        checks["db"] = f"error: {exc}"
        healthy = False

    # Redis check (no-op until Redis is added in Phase 3)
    # When Redis is wired in, add:
    #   r = await get_redis()
    #   await r.ping()

    if not healthy:
        response.status_code = 503

    return {
        "status": "ok" if healthy else "degraded",
        "checks": checks,
        "version": "1.0.0",
    }
```

---

## Step 7 — Update `docker-compose.yml`

Three changes:

**1. API healthcheck** — add a healthcheck that Railway and compose both use:
```yaml
api:
  ...
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 15s
```

**2. Scraper command** — update to use the CLI:
```yaml
scraper:
  command: fedscrape scrape
```

**3. MCP command** — update to use the CLI:
```yaml
mcp:
  command: fedscrape mcp-serve
  environment:
    API_BASE_URL: http://fedscrape_api:8000  # internal Docker network hostname
```

**4. API command** — update to use the CLI:
```yaml
api:
  command: fedscrape serve --host 0.0.0.0
```

---

## Step 8 — Update `Dockerfile`

The Dockerfile currently runs scripts directly. Update it to install the
package properly so all CLI commands are available:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install in editable mode so `fedscrape` CLI is available
COPY pyproject.toml .
COPY requirements.txt .
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

RUN mkdir -p scrape

EXPOSE 8000 8001

# Default command — Railway overrides per-service via Procfile or service config
CMD ["fedscrape", "serve", "--host", "0.0.0.0"]
```

Note: `curl` is added to the base image so the Docker healthcheck works.

---

## Step 9 — Validation

After all changes, verify the following work from the repo root with the
package installed (`pip install -e .`):

```bash
# CLI is importable and shows help
fedscrape --help

# Each subcommand shows its own help
fedscrape serve --help
fedscrape scrape --help
fedscrape mcp-serve --help

# Dry run scrape works without a DB connection
fedscrape scrape --dry-run

# All tests pass
pytest tests/ -v

# Docker compose builds cleanly
docker-compose build

# API starts and health check passes
docker-compose up -d db api
curl http://localhost:8000/health
# Expected: {"status": "ok", "checks": {"db": "ok"}, "version": "1.0.0"}
```

---

## What NOT to change

- `api/services/scraper.py` — scraping logic is correct, do not touch
- `db/models.py` — schema is correct, do not touch
- `db/crud.py` — query helpers are correct, do not touch
- `api/routes/rates.py` — rate endpoints are correct, do not touch
- `api/models/rate.py` — Pydantic schemas are correct, do not touch
- `mcp/server.py` tool definitions — only change the `API_BASE` line and
  remove the `__main__` block, leave all tool logic intact
- Test logic in `tests/test_core.py` — only update imports if package
  paths change as a result of this refactor

---

## Summary of new files

```
fedscrape/
├── __init__.py          (new)
└── cli.py               (new — Typer CLI with serve, scrape, mcp-serve commands)
mcp/
└── server_impl.py       (new — importable run_mcp_server() for CLI)
pyproject.toml           (new — replaces requirements.txt as canonical deps)
```

## Summary of changed files

```
requirements.txt         — replace contents with just: -e .
api/config.py            — add API_BASE_URL setting
api/routes/health.py     — real dependency health checks, 503 on failure
api/services/run_scrape.py — thin shim, logic moved to CLI
mcp/server.py            — API_BASE from config, remove __main__ block
docker-compose.yml       — use fedscrape CLI commands, add healthcheck
Dockerfile               — pip install -e ., add curl
.env.example             — add API_BASE_URL
```
