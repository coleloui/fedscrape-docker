"""Anthropic-backed chat service with Fed H.15 rate tools."""

import json
import logging

import httpx
from anthropic import AsyncAnthropic

from api.config import settings

logger = logging.getLogger(__name__)

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

_SYSTEM_PROMPT = """\
You are a Federal Reserve interest rate analyst with access to real-time \
H.15 rate data. You can answer questions about current rates, historical \
trends, yield curve analysis, and rate comparisons across any time period.

When answering:
- Always fetch current data before making claims about specific values
- Format rate values as percentages to 2 decimal places (e.g. 5.33%)
- When discussing yield curve shape, always check the 10y-2y spread
- Be concise and data-forward — lead with the numbers, follow with context
- If asked about future rates, be clear you can only provide historical data

Available data: Federal Reserve H.15 release — daily rates from the Fed \
including Fed Funds, Treasury bills, Treasury notes/bonds (nominal and TIPS), \
commercial paper, and bank prime loan rate.\
"""

TOOLS = [
    {
        "name": "list_rate_types",
        "description": "List all available Fed H.15 rate type slugs.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_latest_rates",
        "description": "Return the most recent Fed H.15 rate record (all rate types).",
        "input_schema": {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional subset of rate type slugs to include in the response.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_rate_series",
        "description": "Return a time series for a single rate type slug.",
        "input_schema": {
            "type": "object",
            "properties": {
                "rate_type": {
                    "type": "string",
                    "description": "Rate type slug (e.g. treasury_10y).",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of records to return (1–365, default 30).",
                },
            },
            "required": ["rate_type"],
        },
    },
    {
        "name": "get_rate_average",
        "description": "Return the mean of the most recent N values for a rate type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "rate_type": {
                    "type": "string",
                    "description": "Rate type slug.",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of recent records to average (default 30).",
                },
            },
            "required": ["rate_type"],
        },
    },
    {
        "name": "get_yield_spread",
        "description": "Compute the spread (rate_a − rate_b) from the latest record.",
        "input_schema": {
            "type": "object",
            "properties": {
                "rate_a": {
                    "type": "string",
                    "description": "First rate type slug.",
                },
                "rate_b": {
                    "type": "string",
                    "description": "Second rate type slug.",
                },
            },
            "required": ["rate_a", "rate_b"],
        },
    },
]


async def _execute_tool(name: str, tool_input: dict, base_url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            if name == "list_rate_types":
                return json.dumps(_RATE_TYPES)

            elif name == "get_latest_rates":
                resp = await http.get(f"{base_url}/rates/latest")
                resp.raise_for_status()
                data = resp.json()
                fields = tool_input.get("fields")
                if fields:
                    data = {k: v for k, v in data.items() if k == "date" or k in fields}
                return json.dumps(data)

            elif name == "get_rate_series":
                rate_type = tool_input["rate_type"]
                limit = tool_input.get("limit", 30)
                resp = await http.get(
                    f"{base_url}/rates/{rate_type}", params={"limit": limit}
                )
                resp.raise_for_status()
                return json.dumps(resp.json())

            elif name == "get_rate_average":
                rate_type = tool_input["rate_type"]
                days = tool_input.get("days", 30)
                resp = await http.get(
                    f"{base_url}/rates/{rate_type}", params={"limit": days}
                )
                resp.raise_for_status()
                entries = resp.json().get("data", [])
                values = []
                for entry in entries:
                    v = entry.get("value")
                    if v and v != "n.a.":
                        try:
                            values.append(float(v))
                        except (TypeError, ValueError):
                            pass
                avg = sum(values) / len(values) if values else None
                return json.dumps({"rate_type": rate_type, "days": days, "average": avg})

            elif name == "get_yield_spread":
                resp = await http.get(
                    f"{base_url}/rates/spread",
                    params={"rate_a": tool_input["rate_a"], "rate_b": tool_input["rate_b"]},
                )
                resp.raise_for_status()
                return json.dumps(resp.json())

            else:
                return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as exc:
        logger.warning("Tool %s failed: %s", name, exc)
        return json.dumps({"error": str(exc)})


async def run_chat(messages: list[dict]) -> dict:
    """
    Run a tool-augmented chat turn against the Anthropic API.

    Accepts the full conversation history (list of role/content dicts).
    Loops until Claude stops requesting tool calls.
    Returns {"message": str, "tool_calls_made": int}.
    """
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    base_url = f"http://localhost:{settings.PORT}"
    tool_calls_made = 0
    msgs = list(messages)

    while True:
        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            tools=TOOLS,
            messages=msgs,
        )

        if response.stop_reason == "tool_use":
            assistant_content = []
            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })
            msgs.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made += 1
                    logger.info("Tool call: %s", block.name)
                    result_str = await _execute_tool(block.name, block.input, base_url)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    })
            msgs.append({"role": "user", "content": tool_results})

        else:
            text = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            return {"message": text, "tool_calls_made": tool_calls_made}
