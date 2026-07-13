"""Chat endpoint — conversational interface over rate data."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from api.limiter import limiter
from api.services.chat import run_chat

router = APIRouter(prefix="/chat", tags=["chat"])


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    message: str
    tool_calls_made: int


@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Send a message and receive a data-backed response from Claude.

    The client maintains conversation history and sends the full messages
    array on each request. The last message must have role='user'.
    """
    if not body.messages or body.messages[-1].role != "user":
        raise HTTPException(status_code=422, detail="Last message must be role='user'")

    if len(body.messages) > 20:
        raise HTTPException(status_code=422, detail="Maximum 20 messages per request")

    result = await run_chat([m.model_dump() for m in body.messages])
    return ChatResponse(**result)
