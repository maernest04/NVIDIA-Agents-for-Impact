import json
from typing import List, Tuple

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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


def build_agent() -> AgentExecutor:
    llm = ChatNVIDIA(
        model=MODEL,
        api_key=settings.nemotron_api_key,
        base_url=settings.nemotron_base_url,
        temperature=0.2,
    )
    tools = [
        assess_urgency,
        triage_situation,
        search_resources,
        get_resource_by_name,
        draft_outreach_message,
    ]
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=8)


class _ToolCallCollector(BaseCallbackHandler):
    """Captures tool names and triage categories during an agent run."""

    def __init__(self):
        self.tool_calls: List[str] = []
        self.categories: List[str] = []
        self._last_tool: str = ""

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized.get("name", "")
        self.tool_calls.append(name)
        self._last_tool = name

    def on_tool_end(self, output, **kwargs):
        if self._last_tool == "triage_situation":
            try:
                parsed = json.loads(str(output))
                self.categories = parsed.get("identified_categories", [])
            except Exception:
                pass


def run_agent(
    executor: AgentExecutor,
    message: str,
    history: List[dict] = None,
) -> Tuple[str, List[str], List[str]]:
    """Run the agent synchronously.

    Returns:
        (response_text, tool_calls, categories)
        - tool_calls: ordered list of tool names the agent invoked
        - categories: resource categories identified by triage_situation
    """
    chat_history = []
    if history:
        for h in history:
            if h["role"] == "user":
                chat_history.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                chat_history.append(AIMessage(content=h["content"]))

    collector = _ToolCallCollector()
    result = executor.invoke(
        {"input": message, "chat_history": chat_history},
        config={"callbacks": [collector]},
    )
    return result["output"], collector.tool_calls, collector.categories
