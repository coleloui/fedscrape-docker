"""Groq-backed chat service with Fed H.15 rate tools."""

import json
import logging

from groq import AsyncGroq

from api.config import settings
from db.crud import get_average, get_latest, get_series
from db.models import RATE_TYPES
from db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

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

# OpenAI/Groq tool format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_rate_types",
            "description": "List all available Fed H.15 rate type slugs.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_rates",
            "description": "Return the most recent Fed H.15 rate record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional subset of rate type slugs to include."
                        ),
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_rate_series",
            "description": "Return a time series for a single rate type slug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rate_type": {
                        "type": "string",
                        "description": "Rate type slug (e.g. treasury_10y).",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Records to return (1-365, default 30).",
                    },
                },
                "required": ["rate_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_rate_average",
            "description": "Return the mean of the most recent N values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rate_type": {
                        "type": "string",
                        "description": "Rate type slug.",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Recent records to average (default 30).",
                    },
                },
                "required": ["rate_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yield_spread",
            "description": "Compute spread (rate_a - rate_b) from latest record.",
            "parameters": {
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
    },
]


async def _execute_tool(name: str, tool_input: dict) -> str:
    try:
        if name == "list_rate_types":
            return json.dumps(RATE_TYPES)

        elif name == "get_latest_rates":
            async with AsyncSessionLocal() as session:
                record = await get_latest(session)
            if record is None:
                return json.dumps({"error": "No rate data available."})
            data = record.model_dump(mode="json")
            fields = tool_input.get("fields")
            if fields:
                data = {k: v for k, v in data.items() if k == "date" or k in fields}
            return json.dumps(data)

        elif name == "get_rate_series":
            rate_type = tool_input["rate_type"]
            limit = tool_input.get("limit", 30)
            async with AsyncSessionLocal() as session:
                rows = await get_series(session, rate_type, limit)
            return json.dumps({
                "rate_type": rate_type,
                "data": [{"date": str(r["date"]), "value": r["value"]} for r in rows],
            })

        elif name == "get_rate_average":
            rate_type = tool_input["rate_type"]
            days = tool_input.get("days", 30)
            async with AsyncSessionLocal() as session:
                avg = await get_average(session, rate_type, days)
            return json.dumps({"rate_type": rate_type, "days": days, "average": avg})

        elif name == "get_yield_spread":
            rate_a = tool_input["rate_a"]
            rate_b = tool_input["rate_b"]
            async with AsyncSessionLocal() as session:
                record = await get_latest(session)
            if record is None:
                return json.dumps({"error": "No rate data available."})
            val_a = getattr(record, rate_a)
            val_b = getattr(record, rate_b)
            try:
                spread = float(val_a) - float(val_b)
            except (TypeError, ValueError):
                return json.dumps(
                    {"error": "Cannot compute spread — rate unavailable (n.a.)."}
                )
            return json.dumps({
                "date": str(record.date),
                "rate_a": rate_a,
                "rate_b": rate_b,
                "spread": spread,
            })

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as exc:
        logger.warning("Tool %s failed: %s", name, exc)
        return json.dumps({"error": str(exc)})


async def run_chat(messages: list[dict]) -> dict:
    """
    Run a tool-augmented chat turn against the Groq API.

    Accepts the full conversation history (list of role/content dicts).
    Loops until the model stops requesting tool calls.
    Returns {"message": str, "tool_calls_made": int}.
    """
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    tool_calls_made = 0
    msgs: list[dict] = list(messages)

    while True:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=4096,
            messages=[{"role": "system", "content": _SYSTEM_PROMPT}] + msgs,
            tools=TOOLS,
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            message = choice.message
            # content may be None when tool_calls are present
            msgs.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # Execute each tool and append results as role="tool" messages
            for tc in message.tool_calls:
                tool_calls_made += 1
                logger.info("Tool call: %s", tc.function.name)
                tool_input = json.loads(tc.function.arguments)
                result_str = await _execute_tool(tc.function.name, tool_input)
                msgs.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })

        else:
            return {
                "message": choice.message.content or "",
                "tool_calls_made": tool_calls_made,
            }
