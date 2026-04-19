import json
import re

from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.structuring.prompts import build_relationships_prompt


def recognize_relationships(
    components: list[dict],
    visual_elements: list[dict],
    llm: LLMClient | None = None,
) -> list[dict]:
    if llm is None:
        llm = ClaudeClient()

    prompt = build_relationships_prompt(components, {"visual_elements": visual_elements})
    raw = llm.generate(prompt)

    return _parse_relationships(raw)


def _parse_relationships(text: str) -> list[dict]:
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    return []
