import json
import re

from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.structuring.prompts import build_relationships_prompt
from core.structuring.parser import safe_parse_json


def recognize_relationships(
    components: list[dict],
    data,
    llm: LLMClient | None = None,
) -> list[dict]:
    if llm is None:
        llm = ClaudeClient()

    prompt = build_relationships_prompt(components, {
        "relationship_hints": [rh.model_dump(by_alias=True) for rh in data.relationship_hints],
        "detected_keywords": [k.model_dump() for k in data.detected_keywords],
    })
    raw = llm.generate(prompt)

    return safe_parse_json(raw, expected_type=list)
