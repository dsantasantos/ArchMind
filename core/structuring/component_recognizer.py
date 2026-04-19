import json
import re

from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.structuring.prompts import build_components_prompt


def recognize_components(text_blocks: list[str], llm: LLMClient | None = None) -> list[dict]:
    if llm is None:
        llm = ClaudeClient()

    prompt = build_components_prompt({"text_blocks": text_blocks})
    raw = llm.generate(prompt)

    return _parse_components(raw)


def _parse_components(text: str) -> list[dict]:
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
