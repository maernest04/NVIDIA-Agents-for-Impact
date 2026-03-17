from typing import List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
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
community members at San Jose State University (SJSU). Your role is to help \
people find the right campus resource or crisis hotline for what they are \
experiencing — and to give them a concrete next step they can take right now.

You have four tools. You MUST follow this workflow for every message:

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
  - This gives the user a ready-to-send email draft and phone script.

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


def build_agent():
    llm = ChatNVIDIA(
        model=MODEL,
        api_key=settings.nemotron_api_key,
        base_url=settings.nemotron_base_url,
        temperature=0.2,
    )
    tools = [assess_urgency, triage_situation, search_resources, get_resource_by_name, draft_outreach_message]
    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)


def run_agent(agent, message: str, history: List[dict] = None) -> str:
    """Run the agent with the current message and optional conversation history."""
    messages = []

    # Add prior conversation history so the agent has context
    if history:
        for h in history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                messages.append(AIMessage(content=h["content"]))

    # Add the current user message
    messages.append(HumanMessage(content=message))

    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content
