"""
Tests for get_latest completeness filter and chat system prompt guardrails.
"""

import datetime

import pytest

from api.services.chat import _SYSTEM_PROMPT
from db.crud import get_latest, upsert_record
from db.models import RateRecord
from db.session import AsyncSessionLocal

# ---------------------------------------------------------------------------
# System prompt unit tests (no network, no DB)
# ---------------------------------------------------------------------------


def test_system_prompt_fedrate_identity():
    assert "FedRate" in _SYSTEM_PROMPT


def test_system_prompt_scope_restriction():
    assert "You ONLY answer questions related to Federal Reserve" in _SYSTEM_PROMPT


def test_system_prompt_contains_refusal_message():
    assert "I'm FedRate, a specialized Fed rate research assistant" in _SYSTEM_PROMPT


def test_system_prompt_blocks_coding():
    assert "coding" in _SYSTEM_PROMPT


def test_system_prompt_blocks_crypto():
    assert "crypto" in _SYSTEM_PROMPT


def test_system_prompt_no_financial_advice():
    assert "financial advice" in _SYSTEM_PROMPT


def test_system_prompt_informational_disclaimer():
    assert "informational purposes only" in _SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Chat route validation tests (no DB, no Groq API needed)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_rejects_empty_messages(client):
    response = await client.post("/chat", json={"messages": []})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_rejects_non_user_last_message(client):
    response = await client.post(
        "/chat",
        json={"messages": [{"role": "assistant", "content": "Hi"}]},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_rejects_too_many_messages(client):
    messages = [{"role": "user", "content": f"msg {i}"} for i in range(21)]
    response = await client.post("/chat", json={"messages": messages})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# get_latest completeness tests (requires Postgres — skipped without a DB)
# ---------------------------------------------------------------------------


def _make_record(date: datetime.date, complete: bool) -> RateRecord:
    """Build a RateRecord. complete=True fills core Treasury rates."""
    kwargs: dict = {"date": date}
    if complete:
        kwargs.update(treasury_10y="4.50", treasury_2y="4.80", treasury_1y="5.10")
    return RateRecord(**kwargs)


@pytest.mark.asyncio
async def test_get_latest_returns_none_when_no_complete_record(async_client):
    async with AsyncSessionLocal() as session:
        incomplete = _make_record(datetime.date(2024, 1, 1), complete=False)
        await upsert_record(session, incomplete)
        result = await get_latest(session)
    assert result is None


@pytest.mark.asyncio
async def test_get_latest_skips_incomplete_returns_most_recent_complete(async_client):
    async with AsyncSessionLocal() as session:
        # older complete record
        complete = _make_record(datetime.date(2024, 1, 1), complete=True)
        await upsert_record(session, complete)
        # newer but incomplete — should be skipped
        incomplete = _make_record(datetime.date(2024, 1, 2), complete=False)
        await upsert_record(session, incomplete)
        result = await get_latest(session)
    assert result is not None
    assert result.date == datetime.date(2024, 1, 1)
    assert result.treasury_10y == "4.50"


@pytest.mark.asyncio
async def test_get_latest_returns_most_recent_when_multiple_complete(async_client):
    async with AsyncSessionLocal() as session:
        older = _make_record(datetime.date(2024, 1, 1), complete=True)
        newer = _make_record(datetime.date(2024, 1, 3), complete=True)
        await upsert_record(session, older)
        await upsert_record(session, newer)
        result = await get_latest(session)
    assert result is not None
    assert result.date == datetime.date(2024, 1, 3)
