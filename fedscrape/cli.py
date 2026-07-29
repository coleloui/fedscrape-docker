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


_BACKFILL_SERIES_FIELDS: dict[str, list[str]] = {
    "federal_eff_funds": ["federal_funds"],
    "commercial_paper_nonfinancial": [
        "cp_nonfinancial_1m",
        "cp_nonfinancial_2m",
        "cp_nonfinancial_3m",
    ],
    "commercial_paper_financial": [
        "cp_financial_1m",
        "cp_financial_2m",
        "cp_financial_3m",
    ],
    "bank_prime_loan": ["bank_prime_loan"],
    "discount_window_primary_credit": ["discount_window_primary"],
    "us_gov_securities_tresury_bills": [
        "tbill_4w",
        "tbill_3m",
        "tbill_6m",
        "tbill_1y",
    ],
    "maturities_nominal_9": [
        "treasury_1m",
        "treasury_3m",
        "treasury_6m",
        "treasury_1y",
        "treasury_2y",
        "treasury_3y",
        "treasury_5y",
        "treasury_7y",
        "treasury_10y",
        "treasury_20y",
        "treasury_30y",
    ],
    "maturities_inflation_indexed": [
        "tips_5y",
        "tips_7y",
        "tips_10y",
        "tips_20y",
        "tips_30y",
    ],
    "inflation_indexed_long_term": ["inflation_long_term"],
}

_FED_DOWNLOAD_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx"
    "?rel=H15&series={series}&lastobs=&startdate={from_date}&enddate={to_date}"
    "&filetype=csv&label=include&layout=seriescolumn"
)

_NA_VALUES = {"n.a.", "ND", "", "nan", "N/A"}


def _csv_text_from_response(response: object) -> str:
    """Return CSV text from response, unpacking ZIP if needed."""
    import io
    import zipfile

    import requests as _req

    r: _req.Response = response  # type: ignore[assignment]
    content_type = r.headers.get("Content-Type", "")
    if "zip" in content_type or r.content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            names = zf.namelist()
            csv_names = [n for n in names if n.endswith(".csv")]
            target = csv_names[0] if csv_names else names[0]
            return zf.read(target).decode("utf-8", errors="replace")
    return r.text


@app.command()
def backfill(
    start: str = typer.Option(..., "--start", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", help="End date (YYYY-MM-DD)"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Parse without writing to DB"
    ),
) -> None:
    """
    Download historical Fed H.15 data for a date range and upsert into the database.

    Exit codes:
        0 — success
        1 — download, parse, or DB error
    """
    import datetime
    import io
    import re

    import pandas as pd
    import requests

    _setup_logging()
    logger = logging.getLogger("fedscrape.backfill")

    try:
        start_date = datetime.date.fromisoformat(start)
        end_date = datetime.date.fromisoformat(end)
    except ValueError as exc:
        logger.error("Invalid date format: %s", exc)
        raise typer.Exit(code=1)

    from_param = start_date.strftime("%m/%d/%Y")
    to_param = end_date.strftime("%m/%d/%Y")

    from api.services.downloader import SERIES

    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    # Accumulate {date -> {field: value}} across all series
    merged: dict[datetime.date, dict[str, str | None]] = {}

    for series_name, series_id in SERIES.items():
        fields = _BACKFILL_SERIES_FIELDS.get(series_name)
        if not fields:
            logger.warning("No field mapping for series %r — skipping.", series_name)
            continue

        url = _FED_DOWNLOAD_URL.format(
            series=series_id, from_date=from_param, to_date=to_param
        )
        logger.info("Downloading %s...", series_name)

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logger.error("Failed to download %s: %s", series_name, exc)
            raise typer.Exit(code=1)

        content_type = response.headers.get("Content-Type", "")
        logger.info(
            "%s — status=%s Content-Type=%r preview=%r",
            series_name,
            response.status_code,
            content_type,
            response.text[:500],
        )

        try:
            csv_text = _csv_text_from_response(response)
        except Exception as exc:
            logger.error("Could not extract CSV from %s response: %s", series_name, exc)
            raise typer.Exit(code=1)

        try:
            df = pd.read_csv(io.StringIO(csv_text), header=None, dtype=str)
        except Exception as exc:
            logger.error("pandas failed on %s: %s", series_name, exc)
            raise typer.Exit(code=1)

        df = df[df.iloc[:, 0].str.match(date_pattern, na=False)]

        if df.empty:
            logger.warning("No data rows for %s.", series_name)
            continue

        expected_cols = 1 + len(fields)
        if df.shape[1] < expected_cols:
            logger.warning(
                "Series %s: expected %d columns, got %d — skipping.",
                series_name,
                expected_cols,
                df.shape[1],
            )
            continue

        for _, row in df.iterrows():
            try:
                date = datetime.date.fromisoformat(str(row.iloc[0]).strip())
            except ValueError:
                continue
            if date not in merged:
                merged[date] = {}
            for i, field in enumerate(fields):
                raw = str(row.iloc[i + 1]).strip()
                merged[date][field] = None if raw in _NA_VALUES else raw

        logger.info("Parsed %d rows for %s.", len(df), series_name)

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
