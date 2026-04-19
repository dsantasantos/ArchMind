import os

import anthropic

from infra.llm.base import LLMClient


class ClaudeClient(LLMClient):
    def __init__(self):
        api_key = os.environ.get("LLM_API_KEY")
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
