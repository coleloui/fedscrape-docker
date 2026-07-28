# Testing

Pytest + pytest-asyncio, `asyncio_mode = "auto"` (set in `pyproject.toml`
— test functions don't need `@pytest.mark.asyncio` in theory, but the
existing suite adds it explicitly anyway; follow that convention for
consistency rather than relying on the auto mode silently).

## Fixtures (`tests/conftest.py`)

Two client fixtures, deliberately different:

- **`client`** — `httpx.AsyncClient` wired directly to the FastAPI app via
  `ASGITransport`, no DB lifecycle management. Use this for anything that
  doesn't need real data (404s, validation errors, scraper unit tests
  that happen to also hit a route).
- **`async_client`** — same transport, but calls `init_db()` on setup
  (creates tables) and drops all tables on teardown. Use this when a test
  actually needs to read/write rows. Requires a real Postgres reachable at
  `DATABASE_URL` — this fixture will hang or fail without one (see
  "Running without a database" below).

Neither fixture seeds data. If a test needs specific rows in place,
insert them explicitly at the top of the test body via `db.crud`
functions, not by relying on whatever's already in the DB.

## Running without a database

CI (`.github/workflows/ci.yml`) spins up real `postgres:16-alpine` and
`redis:7-alpine` service containers, so the full suite runs against real
services there. Locally — especially from WSL without Docker
integration — you often won't have Postgres reachable, and
`async_client`-based tests will hang on connection or time out.

The existing route smoke tests in `test_core.py` are written to tolerate
this: `test_health_returns_json` accepts `200` *or* `503`,
`test_latest_rates_without_db` wraps the request in a bare `try/except`
because Starlette can re-raise the underlying connection error through
the ASGI transport even after emitting a 500. **Follow this pattern for
new smoke tests that don't strictly require data** — assert on the shape
of whatever comes back rather than requiring a specific status code, so
the test suite stays runnable in a DB-less dev environment. Tests that
inherently need real data (e.g. verifying an actual computed average)
should use `async_client` and simply won't pass without Postgres — that's
expected, not a bug to work around.

## What to test when adding an endpoint

Minimum bar, matching the existing coverage in `test_core.py`:

1. Unknown/invalid path or query params return `404` (see
   `test_unknown_rate_type_returns_404`, `test_spread_unknown_rate_returns_404`)
   — every route that validates against `RATE_TYPES` should have one of
   these.
2. A happy-path smoke test using `client` (not `async_client`) that
   tolerates the no-DB case per the pattern above, unless the endpoint is
   read-only and trivially safe to test with `async_client`.
3. Any new pure logic (parsing, formatting, math) gets a plain sync unit
   test with no fixtures at all — see `test_month_to_number_valid` /
   `test_month_to_number_invalid` for the shape.

## Frontend

`fedscrape-ui` has no test suite yet (no Vitest/Jest/Playwright
configured). Verification for frontend changes currently relies on `tsc
-b`, `eslint`, `npm run build`, and manual/headless browser checks against
the live backend — there's no automated regression suite to run before
committing frontend changes. If this becomes painful, Vitest + React
Testing Library would be the natural addition (matches the Vite setup
already in place), but it hasn't been set up.
