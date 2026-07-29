"""
FedScrape CLI — application entrypoints.

    fedscrape serve       Start the API server
    fedscrape scrape      Fetch the latest Fed H.15 data and upsert into DB
    fedscrape mcp-serve   Start the MCP server (stdio transport)
"""

import asyncio
import logging

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
    port: int = typer.Option(8000, envvar="API_PORT", help="Bind port"),
    reload: bool = typer.Option(False, help="Enable auto-reload (dev only)"),
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
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Parse without writing to DB"
    ),
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
        from db.crud import upsert_records
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
                count = await upsert_records(session, records)
            logger.info("Upserted %d records.", count)
            return 0
        except Exception as exc:
            logger.exception("DB upsert failed: %s", exc)
            return 1

    exit_code = asyncio.run(_run())
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


# FRED series ID → RateRecord field name
_FRED_SERIES: dict[str, str] = {
    "DFF": "federal_funds",
    "DGS2": "treasury_2y",
    "DGS3": "treasury_3y",
    "DGS5": "treasury_5y",
    "DGS7": "treasury_7y",
    "DGS10": "treasury_10y",
    "DGS20": "treasury_20y",
    "DGS30": "treasury_30y",
    "DTB4WK": "tbill_4w",
    "DTB3": "tbill_3m",
    "DTB6": "tbill_6m",
    "DTB1YR": "tbill_1y",
    "DPRIME": "bank_prime_loan",
    "DFII5": "tips_5y",
    "DFII7": "tips_7y",
    "DFII10": "tips_10y",
    "DFII20": "tips_20y",
    "DFII30": "tips_30y",
}

_FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


@app.command()
def backfill(
    start: str = typer.Option(..., "--start", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", help="End date (YYYY-MM-DD)"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Parse without writing to DB"
    ),
) -> None:
    """
    Download historical Fed rate data from FRED and upsert into the database.

    Requires FRED_API_KEY to be set. Fields not available on FRED
    (commercial paper, discount window, short Treasuries, inflation
    long-term average) are left null and can be filled by fedscrape scrape.

    Exit codes:
        0 — success
        1 — download, parse, or DB error
    """
    import datetime

    import requests

    _setup_logging()
    logger = logging.getLogger("fedscrape.backfill")

    try:
        datetime.date.fromisoformat(start)
        datetime.date.fromisoformat(end)
    except ValueError as exc:
        logger.error("Invalid date format: %s", exc)
        raise typer.Exit(code=1)

    from api.config import settings

    if not settings.FRED_API_KEY:
        logger.error("FRED_API_KEY is not set.")
        raise typer.Exit(code=1)

    # Accumulate {date -> {field: value}} across all series
    merged: dict[datetime.date, dict[str, str | None]] = {}

    for series_id, field in _FRED_SERIES.items():
        logger.info("Fetching FRED %s → %s...", series_id, field)
        try:
            resp = requests.get(
                _FRED_BASE_URL,
                params={
                    "series_id": series_id,
                    "observation_start": start,
                    "observation_end": end,
                    "api_key": settings.FRED_API_KEY,
                    "file_type": "json",
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logger.error("Failed to fetch %s: %s", series_id, exc)
            raise typer.Exit(code=1)

        observations = resp.json().get("observations", [])
        count = 0
        for obs in observations:
            raw_date = obs.get("date", "")
            raw_value = obs.get("value", "")
            try:
                date = datetime.date.fromisoformat(raw_date)
            except ValueError:
                continue
            if date not in merged:
                merged[date] = {}
            merged[date][field] = None if raw_value in {".", ""} else raw_value
            count += 1

        logger.info("Parsed %d observations for %s.", count, series_id)

    if not merged:
        logger.warning("No records parsed.")
        raise typer.Exit(code=1)

    from db.models import RateRecord

    records = [
        RateRecord(date=date, **fields_dict)
        for date, fields_dict in sorted(merged.items())
    ]
    logger.info("Total: %d records to upsert.", len(records))

    if dry_run:
        logger.info("Dry run — skipping DB upsert.")
        return

    async def _run() -> int:
        from db.crud import upsert_records
        from db.session import AsyncSessionLocal, init_db

        try:
            await init_db()
            async with AsyncSessionLocal() as session:
                count = await upsert_records(session, records)
            logger.info("Upserted %d records.", count)
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
    from fedscrape.mcp_server import run_mcp_server

    asyncio.run(run_mcp_server())
