# Deployment Guide — Railway

## Prerequisites

- Railway account and CLI (`npm i -g @railway/cli`)
- Docker Desktop (for local testing)

---

## Local development

```bash
# Install in editable mode
pip install -e ".[dev]"

# Copy env vars
cp .env.example .env
# Edit .env — set DATABASE_URL to a local Postgres instance

# Start Postgres + Redis + API
docker compose up -d db redis api

# Verify health
curl http://localhost:8000/health
# {"status":"ok","checks":{"db":"ok"},"version":"1.0.0"}

# Run a scrape
fedscrape scrape

# Run tests
pytest tests/ -v
```

---

## Railway setup

### 1. Create a project

```bash
railway login
railway init
```

### 2. Add a Postgres database

In the Railway dashboard: **New Service → Database → PostgreSQL**.
Railway automatically injects `DATABASE_URL` into all services.

### 3. Add a Redis database

In the Railway dashboard: **New Service → Database → Redis**.
Railway automatically injects `REDIS_URL` into all services.

### 4. Create three services from the same repo

For each service, connect it to your GitHub repo and set the start command
from the corresponding file in `railway/`:

| Service  | Start command | Config file |
|---|---|---|
| api      | `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT` | `railway/api.json` |
| scraper  | `fedscrape scrape` | `railway/scraper.json` |
| mcp      | `fedscrape mcp-serve` | `railway/mcp.json` |

### 5. Schedule the scraper

In the Railway dashboard, set the scraper service to a **Cron** service type:

- Schedule: `0 18 * * 1-5` (weekdays at 6 PM UTC — after Fed H.15 publishes)
- To trigger a manual scrape: Railway dashboard → scraper service → **Run Now**

### 6. Set environment variables per service

**api service:**

| Variable | Value |
|---|---|
| `DATABASE_URL` | Auto-injected by Railway Postgres plugin |
| `REDIS_URL` | Auto-injected by Railway Redis plugin |
| `PORT` | Auto-injected by Railway |
| `API_BASE_URL` | `http://<api-service-name>.railway.internal:$PORT` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` |
| `ADMIN_API_KEY` | A secret key for admin endpoints |
| `SECRET_KEY` | A random secret for signing |

**scraper service:**

| Variable | Value |
|---|---|
| `DATABASE_URL` | Auto-injected by Railway Postgres plugin |

**mcp service:**

| Variable | Value |
|---|---|
| `API_BASE_URL` | Internal Railway URL of the api service |

### 7. Health check

Railway auto-detects `/health`. Confirm the endpoint returns 200:

```bash
curl https://<your-app>.railway.app/health
```

### 8. Custom domain

Railway dashboard → api service → **Settings → Domains → Generate Domain**
or add a custom domain and follow the CNAME instructions.

---

## GitHub Actions CI/CD

The `.github/workflows/ci.yml` workflow:
- Runs the test suite on every push and pull request to `main`
- Triggers a Railway redeploy on successful pushes to `main`

### Required GitHub secrets

| Secret | How to get it |
|---|---|
| `RAILWAY_DEPLOY_WEBHOOK` | Railway dashboard → api service → **Settings → Deploy Webhooks → Generate** |

Add secrets at: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

---

## Environment variables reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | `postgresql+asyncpg://...` connection string |
| `REDIS_URL` | Yes | `redis://localhost:6379` | Redis for caching and rate limiting |
| `PORT` | No | `8000` | Port the API listens on (Railway injects this) |
| `API_PORT` | No | `8000` | Legacy alias for PORT |
| `API_BASE_URL` | Yes (MCP/chat) | `http://localhost:8000` | URL the MCP/chat service uses to reach the API |
| `ANTHROPIC_API_KEY` | Yes (chat) | `` | Key for the `/chat` endpoint |
| `ANTHROPIC_MODEL` | No | `claude-sonnet-4-6` | Claude model for the chat endpoint |
| `AWS_KEY` | No | `` | S3 uploads (leave blank to skip) |
| `AWS_SECRET` | No | `` | S3 uploads |
| `AWS_REGION` | No | `` | S3 uploads |
| `S3_BUCKET` | No | `` | S3 uploads |

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check (200 / 503) |
| `GET` | `/rates/latest` | Most recent H.15 record (cached 1 h) |
| `GET` | `/rates/spread?rate_a=treasury_10y&rate_b=treasury_2y` | Yield spread (cached 1 h) |
| `POST` | `/rates/refresh` | Trigger scrape + upsert, clears cache |
| `GET` | `/rates/{rate_type}?limit=30` | Time series for one rate type (cached 1 h) |
| `POST` | `/chat` | Conversational interface backed by Claude + rate tools |

### Rate limits

| Endpoint | Limit |
|---|---|
| `GET /rates/*` | 60 requests/minute per IP |
| `POST /rates/refresh` | 5 requests/minute per IP |
| `POST /chat` | 20 requests/minute per IP |

### Available rate type slugs

```
federal_funds
cp_nonfinancial_1m  cp_nonfinancial_2m  cp_nonfinancial_3m
cp_financial_1m     cp_financial_2m     cp_financial_3m
bank_prime_loan
discount_window_primary
tbill_4w  tbill_3m  tbill_6m  tbill_1y
treasury_1m  treasury_3m  treasury_6m  treasury_1y  treasury_2y
treasury_3y  treasury_5y  treasury_7y  treasury_10y treasury_20y  treasury_30y
tips_5y  tips_7y  tips_10y  tips_20y  tips_30y
inflation_long_term
```
