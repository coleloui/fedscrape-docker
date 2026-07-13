"""
FedScrape MCP server.

All tools call the FastAPI service via httpx using API_BASE_URL.
This file lives in fedscrape/ (not mcp/) to avoid shadowing the
`mcp` PyPI package namespace.
"""

import json
import logging

import httpx
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from api.config import settings

logger = logging.getLogger(__name__)

server = Server("fedscrape")

_RATE_TYPES = [
    "federal_funds",
    "cp_nonfinancial_1m", "cp_nonfinancial_2m", "cp_nonfinancial_3m",
    "cp_financial_1m", "cp_financial_2m", "cp_financial_3m",
    "bank_prime_loan",
    "discount_window_primary",
    "tbill_4w", "tbill_3m", "tbill_6m", "tbill_1y",
    "treasury_1m", "treasury_3m", "treasury_6m",
    "treasury_1y", "treasury_2y", "treasury_3y", "treasury_5y",
    "treasury_7y", "treasury_10y", "treasury_20y", "treasury_30y",
    "tips_5y", "tips_7y", "tips_10y", "tips_20y", "tips_30y",
    "inflation_long_term",
]


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_rate_types",
            description="List all available Fed H.15 rate type slugs.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="get_latest_rates",
            description="Return the most recent Fed H.15 rate record (all rate types).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="get_rate_by_date",
            description="Return the rate record for a specific date (YYYY-MM-DD).",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format.",
                    }
                },
                "required": ["date"],
            },
        ),
        types.Tool(
            name="get_rate_series",
            description="Return a time series for a single rate type slug.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rate_type": {
                        "type": "string",
                        "description": "Rate type slug (e.g. treasury_10y).",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of records to return (1–365, default 30).",
                        "default": 30,
                    },
                },
                "required": ["rate_type"],
            },
        ),
        types.Tool(
            name="get_rate_average",
            description="Return the mean of the most recent N values for a rate type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rate_type": {
                        "type": "string",
                        "description": "Rate type slug.",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of recent records to average (default 30).",
                        "default": 30,
                    },
                },
                "required": ["rate_type"],
            },
        ),
        types.Tool(
            name="get_yield_spread",
            description="Compute the spread (rate_a − rate_b) from the latest record.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rate_a": {"type": "string", "description": "First rate type slug."},
                    "rate_b": {"type": "string", "description": "Second rate type slug."},
                },
                "required": ["rate_a", "rate_b"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    base = settings.API_BASE_URL.rstrip("/")

    async with httpx.AsyncClient(timeout=15.0) as client:
        if name == "list_rate_types":
            result = _RATE_TYPES

        elif name == "get_latest_rates":
            resp = await client.get(f"{base}/rates/latest")
            resp.raise_for_status()
            result = resp.json()

        elif name == "get_rate_by_date":
            d = arguments["date"]
            # Fetch series limited to 365 and filter client-side by date
            rate_type = arguments.get("rate_type", "federal_funds")
            resp = await client.get(
                f"{base}/rates/{rate_type}", params={"limit": 365}
            )
            resp.raise_for_status()
            series = resp.json().get("data", [])
            result = next((r for r in series if r["date"] == d), None)
            if result is None:
                result = {"error": f"No data found for date {d}"}

        elif name == "get_rate_series":
            rate_type = arguments["rate_type"]
            limit = arguments.get("limit", 30)
            resp = await client.get(
                f"{base}/rates/{rate_type}", params={"limit": limit}
            )
            resp.raise_for_status()
            result = resp.json()

        elif name == "get_rate_average":
            rate_type = arguments["rate_type"]
            days = arguments.get("days", 30)
            resp = await client.get(
                f"{base}/rates/{rate_type}", params={"limit": days}
            )
            resp.raise_for_status()
            entries = resp.json().get("data", [])
            values = []
            for entry in entries:
                try:
                    values.append(float(entry["value"]))
                except (TypeError, ValueError):
                    pass
            avg = sum(values) / len(values) if values else None
            result = {"rate_type": rate_type, "days": days, "average": avg}

        elif name == "get_yield_spread":
            rate_a = arguments["rate_a"]
            rate_b = arguments["rate_b"]
            resp = await client.get(
                f"{base}/rates/spread",
                params={"rate_a": rate_a, "rate_b": rate_b},
            )
            resp.raise_for_status()
            result = resp.json()

        else:
            result = {"error": f"Unknown tool: {name}"}

    return [types.TextContent(type="text", text=json.dumps(result, default=str))]


async def run_mcp_server() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
