"""
LangChain-only agent: tool-calling loop with ChatNVIDIA (no LangGraph, no AgentExecutor).
"""
import json
from typing import List, Tuple

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from agent.tools import (
    assess_urgency,
    draft_outreach_message,
    get_resource_by_name,
    search_resources,
    triage_situation,
)
from config import settings

MODEL = "nvidia/nemotron-3-super-120b-a12b"
MAX_ITERATIONS = 8

SYSTEM_PROMPT = """\
You are a compassionate, non-judgmental resource assistant for students and \
community members at San Jose State University (SJSU). Many students feel \
embarrassed or nervous about reaching out for help; your role is to make it \
easy. Help them find the right campus resource or crisis hotline (SJSU-specific \
or national/USA-wide) for what they are experiencing — and give them a \
concrete next step they can take right now (including a draft message they \
can send or say).

You have five tools. You MUST follow this workflow for every message:

STEP 1 — ALWAYS call assess_urgency(message) first, with the user's exact message.
  - If urgency = "immediate": respond with 988 and/or 911 immediately. Express \
    care and urgency. Do NOT call other tools first. End there.
  - If urgency = "elevated" or "standard": continue to Step 2.

STEP 2 — Call triage_situation(user_message) to identify the right resource categories.
  - Use the returned search terms for Step 3.

STEP 3 — Call search_resources(query) for each recommended search term (1–3 calls max).
  - Also call get_resource_by_name(name) if you know a specific resource fits well \
    (e.g. "CAPS" for mental health, "SJSU Cares" for basic needs).

STEP 4 — For non-immediate situations, call draft_outreach_message(resource_name, \
user_situation) using the single most relevant resource.
  - Nemotron will generate a personalized email draft and phone script for the student.

Response format:
- Start with one short empathetic sentence acknowledging what the person shared.
- Present 1–3 relevant resources clearly (bold the name, then phone on the next line).
- Include the outreach draft from draft_outreach_message naturally at the end, \
  under a heading like "Here's a message you can send or say:".
- End every response with: \
  "If this is a life-threatening emergency, please call 911 immediately."

Other rules:
- Never diagnose, prescribe, or give clinical advice.
- Never rely on memory for phone numbers — always use tools.
- Use markdown for structure: bold resource names, paragraph breaks between sections.
- Keep the empathetic intro to 2 sentences max — get to the resources quickly.\
"""


TOOLS = [
    assess_urgency,
    triage_situation,
    search_resources,
    get_resource_by_name,
    draft_outreach_message,
]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}


def build_agent():
    """Return the bound LLM (with tools) for use in run_agent. No executor object."""
    llm = ChatNVIDIA(
        model=MODEL,
        api_key=settings.nemotron_api_key,
        base_url=settings.nemotron_base_url,
        temperature=1.0,
    )
    return llm.bind_tools(TOOLS)


def run_agent(
    bound_llm,
    message: str,
    history: List[dict] = None,
) -> Tuple[str, List[str], List[str]]:
    """
    Run the LangChain tool-calling loop: reason -> act -> observe until done.
    Returns (response_text, tool_calls, categories).
    """
    messages: List = [SystemMessage(content=SYSTEM_PROMPT)]

    if history:
        for h in history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                messages.append(AIMessage(content=h["content"]))

    messages.append(HumanMessage(content=message))

    tool_calls_ordered: List[str] = []
    categories: List[str] = []

    for _ in range(MAX_ITERATIONS):
        response = bound_llm.invoke(messages)
        messages.append(response)

        if not getattr(response, "tool_calls", None):
            return (response.content or ""), tool_calls_ordered, categories

        for tc in response.tool_calls:
            if isinstance(tc, dict):
                name = tc.get("name", "")
                args = tc.get("args") or {}
                tool_call_id = tc.get("id", "")
            else:
                name = getattr(tc, "name", "")
                args = getattr(tc, "args", {}) or {}
                tool_call_id = getattr(tc, "id", "")
            tool_calls_ordered.append(name)

            tool = TOOLS_BY_NAME.get(name)
            if not tool:
                result = f"Unknown tool: {name}"
            else:
                try:
                    result = tool.invoke(args)
                except Exception as e:
                    result = f"Error: {e}"

            if name == "triage_situation":
                try:
                    parsed = json.loads(result)
                    categories = parsed.get("identified_categories", [])
                except Exception:
                    pass

            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call_id)
            )

    # Max iterations reached; get one final response from the model
    final = bound_llm.invoke(messages)
    return (getattr(final, "content", None) or ""), tool_calls_ordered, categories
