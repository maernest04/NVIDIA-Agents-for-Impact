import asyncio
import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.agent.agent import build_agent, run_agent

router = APIRouter(prefix="/chat", tags=["chat"])

# Lazily initialised on first request so the app starts without a valid API key.
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


class HistoryMessage(BaseModel):
    role: str   # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[HistoryMessage]] = None


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@router.post("/")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    history = (
        [{"role": h.role, "content": h.content} for h in request.history]
        if request.history
        else []
    )

    async def generate():
        loop = asyncio.get_event_loop()

        # Run the synchronous LangChain agent in a thread pool so the event
        # loop stays unblocked while Nemotron API calls are in flight.
        try:
            response_text, tool_calls, categories = await loop.run_in_executor(
                None,
                lambda: run_agent(_get_agent(), request.message, history),
            )
        except Exception as exc:
            yield _sse({"type": "error", "message": str(exc)})
            return

        # 1. Emit real tool-call events so the frontend AgentTrace can display
        #    the actual reasoning steps the agent took.
        for tool_name in tool_calls:
            yield _sse({"type": "tool_call", "tool": tool_name})

        # 2. Emit the triage categories detected by Nemotron.
        if categories:
            yield _sse({"type": "categories", "categories": categories})

        # 3. Stream the final response word-by-word via SSE so the frontend
        #    can render it token-by-token without faking it with setInterval.
        words = response_text.split(" ")
        for word in words:
            yield _sse({"type": "token", "content": word + " "})
            await asyncio.sleep(0.03)

        yield _sse({"type": "done"})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
