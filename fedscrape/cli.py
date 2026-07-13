"""
FedScrape CLI — application entrypoints.

    fedscrape serve       Start the API server
    fedscrape scrape      Fetch the latest Fed H.15 data and upsert into DB
    fedscrape mcp-serve   Start the MCP server (stdio transport)
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


@app.command()
def mcp_serve() -> None:
    """Start the FedScrape MCP server (stdio transport)."""
    _setup_logging()
    from fedscrape.mcp_server import run_mcp_server

    asyncio.run(run_mcp_server())
