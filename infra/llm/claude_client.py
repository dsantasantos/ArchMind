import os

import anthropic

from infra.llm.base import LLMClient


class ClaudeClient(LLMClient):
    def __init__(self):
        api_key = os.environ.get("LLM_API_KEY")
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, image_base64: str = None, media_type: str = "image/jpeg") -> str:
        if image_base64:
            content = [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_base64}},
                {"type": "text", "text": prompt},
            ]
        else:
            content = prompt
        response = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text
