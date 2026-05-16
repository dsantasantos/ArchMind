import json
import re

from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.withllm.structuring.prompts import build_architecture_prompt

_FALLBACK = {
    "architecture_style": "unknown",
    "communication_patterns": [],
    "confidence": 0.0,
    "uncertainties": [],
}


def recognize_architecture_style(
    components: list[dict],
    relationships: list[dict],
    context_groups: list[dict] | None = None,
    llm: LLMClient | None = None,
) -> dict:
    if llm is None:
        llm = ClaudeClient()

    prompt = build_architecture_prompt(components, relationships, context_groups)
    raw = llm.generate(prompt)

    return _parse_architecture_result(raw)


def _parse_architecture_result(text: str) -> dict:
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return {**_FALLBACK, **result}
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, dict):
                return {**_FALLBACK, **result}
        except json.JSONDecodeError:
            pass

    return dict(_FALLBACK)
