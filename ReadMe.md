# FedScrape

FastAPI + MCP server that scrapes and serves Federal Reserve H.15 interest rate data. Rates are fetched from the Fed's published release, stored in PostgreSQL, and exposed via a REST API and an MCP (Model Context Protocol) server for LLM tool use.

## Setup

### Docker Compose (recommended)

```
docker-compose up -d --build
```

Configure credentials in `docker-compose.yml` under `python_app -> environment`:

```
DB_USER:
DB_PASSWORD:
DB_PORT:
```

And under `database -> environment`:

```
POSTGRES_USER:
POSTGRES_PASSWORD:
POSTGRES_DB:
```

### Standalone container

```
docker build . -t fedscrape-docker:localhost
docker run -t -d fedscrape-docker:localhost
```

Exec into the container:

```
docker container ls
docker exec -it <CONTAINER_ID> /bin/bash
```

## Commands

The `fedscrape` CLI is the entrypoint for all operations.

```
fedscrape serve          Start the REST API server (default: 0.0.0.0:8000)
fedscrape scrape         Fetch the latest Fed H.15 data and upsert into the DB
fedscrape mcp-serve      Start the MCP server (stdio transport)
```

Options for `fedscrape serve`:

```
--host TEXT        Bind host (default: 0.0.0.0)
--port INTEGER     Bind port (default: 8000, env: API_PORT)
--reload           Enable auto-reload for development
--log-level TEXT   Uvicorn log level (default: info)
```

Options for `fedscrape scrape`:

```
--dry-run          Parse and log records without writing to the database
```

## API

Once the server is running, interactive docs are available at `http://localhost:8000/docs`.

Key endpoints:

```
GET /health          Health check
GET /rates           List interest rates (filterable by series and date range)
```
