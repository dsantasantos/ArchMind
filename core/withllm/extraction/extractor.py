import base64
import json
import re

from infra.llm.claude_client import ClaudeClient
from core.withllm.extraction.prompts import build_extraction_prompt


def extract_from_image(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    llm = ClaudeClient()
    response = llm.generate(build_extraction_prompt(), image_base64=image_base64, media_type=media_type)
    return _parse_json(response)


def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if match:
            return json.loads(match.group(1))
        raise ValueError(f"Could not parse LLM response as JSON: {text[:300]}")
