from typing import List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from agent.tools import get_resource_by_name, search_resources
from config import settings

MODEL = "nvidia/nemotron-3-super-120b-a12b"

SYSTEM_PROMPT = """\
You are a compassionate, non-judgmental resource assistant for students and \
community members at San Jose State University. Your role is to help people \
find the right campus resource or crisis hotline for what they are experiencing.

You have access to a database of SJSU campus resources and national crisis \
hotlines. ALWAYS use your tools to look up resources — never rely on memory \
alone for phone numbers or contact details.

Guidelines:
- Listen carefully and respond with empathy before providing resources.
- If the person mentions immediate danger to themselves or others, prioritize \
  emergency and crisis resources (988, 911, UPD).
- Match resources to what the person actually needs — do not overwhelm them \
  with unrelated options.
- For mental health concerns, always include CAPS (search for it if needed).
- For basic needs (food, housing, money), always include SJSU Cares.
- Keep your response concise: a brief empathetic sentence, then the \
  relevant resource(s) with phone number and what to say when calling.
- Never diagnose, prescribe, or give clinical advice.
- End every response with: \
  "If this is a life-threatening emergency, please call 911 immediately."\
"""


def build_agent():
    llm = ChatNVIDIA(
        model=MODEL,
        api_key=settings.nemotron_api_key,
        base_url=settings.nemotron_base_url,
        temperature=0.2,
    )
    tools = [search_resources, get_resource_by_name]
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
