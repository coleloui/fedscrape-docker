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

# Start Postgres + API
docker compose up -d db api

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
Copy the `DATABASE_URL` from the Variables tab.

### 3. Deploy the API service

```bash
railway up
```

Set these environment variables in Railway → Service → Variables:

| Variable | Value |
|---|---|
| `DATABASE_URL` | (from Railway Postgres — use the `postgresql+asyncpg://` form) |
| `API_PORT` | `8000` |
| `API_BASE_URL` | `http://<your-api-service-name>.railway.internal:8000` |

Set the start command to:
```
fedscrape serve --host 0.0.0.0
```

### 4. Deploy the MCP service (optional)

Add a second service from the same repo. Set:
- Start command: `fedscrape mcp-serve`
- `API_BASE_URL`: internal Railway URL of the API service

### 5. Schedule scrapes with Railway Cron

In the Railway dashboard: **New Service → Cron Job**.

- Command: `fedscrape scrape`
- Schedule: `0 18 * * 1-5` (weekdays at 6 PM UTC — after Fed H.15 publishes)
- Set the same `DATABASE_URL` env var

### 6. Health check

Railway auto-detects `/health`. Confirm the endpoint returns 200:

```bash
curl https://<your-app>.railway.app/health
```

---

## Environment variables reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | `postgresql+asyncpg://...` connection string |
| `API_PORT` | No | `8000` | Port the API listens on |
| `API_BASE_URL` | Yes (MCP) | `http://localhost:8000` | URL the MCP server uses to reach the API |
| `AWS_KEY` | No | `` | S3 uploads (leave blank to skip) |
| `AWS_SECRET` | No | `` | S3 uploads |
| `AWS_REGION` | No | `` | S3 uploads |
| `S3_BUCKET` | No | `` | S3 uploads |

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check (200 / 503) |
| `GET` | `/rates/latest` | Most recent H.15 record |
| `GET` | `/rates/spread?rate_a=treasury_10y&rate_b=treasury_2y` | Yield spread |
| `POST` | `/rates/refresh` | Trigger scrape + upsert |
| `GET` | `/rates/{rate_type}?limit=30` | Time series for one rate type |

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
