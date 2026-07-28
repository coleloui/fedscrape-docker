# Database

PostgreSQL via SQLModel (SQLAlchemy + Pydantic), async throughout
(`asyncpg` driver). See [architecture.md](architecture.md) for where the
DB layer sits relative to the API/service layers.

## Current setup: no migrations yet

There is **no Alembic migration history** in this repo, despite `alembic`
being listed as a dependency in `pyproject.toml`. The schema is created
via `SQLModel.metadata.create_all()` in `db/session.py:init_db()`, called
once on every app startup (`api/main.py`'s `lifespan()`). This is
idempotent and safe to call repeatedly — it only creates tables that
don't already exist, never alters existing ones.

This is a deliberate, current choice, not an oversight: the schema is a
single table (`rate_records`), stable, and there are no production users
yet, so the overhead of a migration workflow isn't worth it right now.
**Do not set up Alembic without being asked** — it was tried once
(scaffolded, then fully reverted) specifically because of this. There's a
`TODO` comment in `api/main.py`'s `lifespan()` marking where to switch:

```python
# TODO: Replace create_all() with Alembic before first schema
# change post-launch. Add Railway release command: alembic upgrade head
await init_db()
```

When that day comes: `alembic init -t async db/alembic` (the async
template — this app only has an `asyncpg` driver, no sync `psycopg2`, so
`env.py` needs to run migrations via `asyncio.run(...)`, not the default
sync connection), point `env.py`'s `target_metadata` at
`SQLModel.metadata` after importing `db.models`, and pull the DB URL from
`api.config.settings.DATABASE_URL` rather than hardcoding
`alembic.ini`'s `sqlalchemy.url`. Since the live DB will already have the
table from `create_all()`, the baseline migration needs `alembic stamp
head` on that environment instead of `alembic upgrade head` (which would
try to `CREATE TABLE` on top of a table that already exists).

## Model (`db/models.py`)

One SQLModel table class, `RateRecord` (`__tablename__ = "rate_records"`):
`id` (autoincrement PK), `date` (unique, indexed), and ~29 `Optional[str]`
columns — one per Fed rate series (`federal_funds`, `treasury_10y`,
`tbill_3m`, etc.). All rate columns are `str`, not `float`, because the
scraper stores the raw H.15 text values verbatim, including the literal
`"n.a."` the Fed uses for unavailable data on a given date. Never widen
these to `float` at the model level — parse defensively at the point of
use instead (see `db/crud.py:get_average()` for the reference pattern:
try/except around `float(v)`, skip on failure).

Two module-level helpers matter for anything touching rate types:

- `SCRAPE_COLUMN_MAP: dict[str, str]` — maps the scraper's raw H.15 HTML
  column header text to the model field name. This is a scraper-to-slug
  mapping, **not** a display-name mapping — don't reuse it for
  human-readable labels (see `api/routes/rates.py:slug_to_display()` for
  the actual display-name logic, which derives labels from the slug
  itself rather than from this map).
- `RATE_TYPES: list[str]` — the ordered list of all valid rate-type slugs
  (every model field except `id`/`date`). This is the single source of
  truth for "is this a valid rate type" — every route that takes a
  `rate_type` path/query param validates against it.

There is no `RATE_COLUMNS` dict with display names anywhere in the
codebase — if you're looking for one (an older draft of this doc's plan
assumed it existed), it doesn't; display names are generated
programmatically.

## CRUD layer (`db/crud.py`)

Plain async functions taking an `AsyncSession` as the first argument, no
repository classes or ORM-session-as-a-field patterns. Key functions:

- `get_latest(session)` — most recent record by `date`.
- `get_series(session, rate_type, limit=30)` — last `limit` (date, value)
  pairs for one column, ordered newest-first.
- `get_average(session, rate_type, days=30)` — mean of the most recent
  `days` non-null, non-`"n.a."` values. **Takes a trailing window
  (`days: int`), not a `start`/`end` date range** — if you're adding a
  date-range average, that's new logic, not a parameter rename.
- `upsert_record`/`upsert_records` — Postgres `ON CONFLICT (date) DO
  UPDATE`, keyed on the unique `date` column. This is how re-scraping the
  same date safely overwrites rather than duplicates.

## Redis

Used only for response caching (see [backend.md](backend.md)'s Caching
section) — never for anything durable. No migration/schema concerns
apply to it.
