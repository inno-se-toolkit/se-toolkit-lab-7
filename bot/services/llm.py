"""LLM service — OpenAI-compatible tool-calling loop."""

import json
import sys

import httpx

from config import settings
from services import lms

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get all labs and tasks from the LMS",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get enrolled students and their groups",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a lab",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier e.g. 'lab-01'"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier e.g. 'lab-01'"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier e.g. 'lab-01'"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group average scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier e.g. 'lab-01'"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by average score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab (students who scored >= 60)",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier e.g. 'lab-01'"}},
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from the autochecker",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

_TOOL_MAP = {
    "get_items": lambda _: lms.get_items(),
    "get_learners": lambda _: lms.get_learners(),
    "get_scores": lambda a: lms.get_scores(a["lab"]),
    "get_pass_rates": lambda a: lms.get_pass_rates(a["lab"]),
    "get_timeline": lambda a: lms.get_timeline(a["lab"]),
    "get_groups": lambda a: lms.get_groups(a["lab"]),
    "get_top_learners": lambda a: lms.get_top_learners(a["lab"], a.get("limit", 10)),
    "get_completion_rate": lambda a: lms.get_completion_rate(a["lab"]),
    "trigger_sync": lambda _: lms.trigger_sync(),
}

_SYSTEM = (
    "You are an LMS analytics assistant. "
    "Use the provided tools to fetch data and answer the user's question. "
    "Always call tools to get real data — never make up numbers. "
    "Be concise and format responses clearly."
)


async def route(user_message: str) -> str:
    messages: list[dict] = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_message},
    ]

    async with httpx.AsyncClient() as client:
        for _ in range(10):  # max 10 rounds
            resp = await client.post(
                f"{settings.llm_api_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={"model": settings.llm_api_model, "messages": messages, "tools": TOOLS},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]
            messages.append(msg)

            if choice["finish_reason"] != "tool_calls":
                return msg.get("content") or "No response."

            # execute tool calls
            tool_calls = msg.get("tool_calls", [])
            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
            for tc in tool_calls:
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"] or "{}")
                print(f"[tool] LLM called: {name}({args})", file=sys.stderr)
                try:
                    result = await _TOOL_MAP[name](args)
                    result_str = json.dumps(result)
                    if len(result_str) > 3000:
                        result_str = result_str[:3000] + "..."
                    print(f"[tool] Result: {result_str[:80]}...", file=sys.stderr)
                except Exception as e:
                    result_str = f"Error: {e}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_str,
                })

    return "Reached maximum reasoning steps. Please try a simpler question."
