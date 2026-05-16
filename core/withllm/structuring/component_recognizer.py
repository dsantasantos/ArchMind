import json
import re

from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.withllm.structuring.prompts import build_components_prompt


def recognize_components(data, llm: LLMClient | None = None) -> list[dict]:
    if llm is None:
        llm = ClaudeClient()

    prompt = build_components_prompt({
        "text_blocks": data.text_blocks,
        "grouped_elements": [e.model_dump() for e in data.grouped_elements],
        "detected_keywords": [k.model_dump() for k in data.detected_keywords],
        "context_groups": [g.model_dump() for g in data.context_groups],
    })
    raw = llm.generate(prompt)

    return _parse_components(raw)


def _parse_components(text: str) -> list[dict]:
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    return []
