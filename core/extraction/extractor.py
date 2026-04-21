import json
import re
from typing import Any

from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.extraction.prompts import build_extraction_prompt


def extract_from_image(
    image_base64: str,
    media_type: str = "image/jpeg",
    llm: LLMClient | None = None,
) -> dict:
    if llm is None:
        llm = ClaudeClient()
    raw = llm.generate(build_extraction_prompt(), image_base64=image_base64, media_type=media_type)
    return _parse_extraction(raw)


def _parse_extraction(text: str) -> dict:
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    raise ValueError("LLM did not return valid JSON extraction output")


def extract(filename: str) -> dict[str, Any]:
    # Mocked extraction — kept for compatibility with the existing upload pipeline
    return {
        "source": filename,
        "raw_elements": ["api_gateway", "service_a", "service_b", "database"],
        "raw_text": "Mocked extraction output",
    }
