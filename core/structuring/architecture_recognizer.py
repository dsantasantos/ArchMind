import json
import re

from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.structuring.prompts import build_architecture_prompt
from core.structuring.parser import safe_parse_json

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

    result = safe_parse_json(raw, expected_type=dict)
    return {**_FALLBACK, **result} if result else dict(_FALLBACK)
