import json
import re

from infra.llm.claude_client import ClaudeClient
from core.withllm.enrichment.prompts import build_enrichment_prompt


def enrich(structured_data: dict) -> dict:
    llm = ClaudeClient()
    prompt = build_enrichment_prompt(structured_data)
    raw = llm.generate(prompt)
    return _parse_json(raw)


def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        if match:
            return json.loads(match.group(1).strip())
        raise ValueError(f"LLM returned invalid JSON: {raw[:200]}")
