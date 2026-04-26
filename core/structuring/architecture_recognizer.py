from infra.llm.base import LLMClient
from infra.llm.claude_client import ClaudeClient
from core.structuring.prompts import build_architecture_prompt


def recognize_architecture_style(
    components: list[dict],
    relationships: list[dict],
    context_groups: list[dict] | None = None,
    llm: LLMClient | None = None,
) -> str:
    if llm is None:
        llm = ClaudeClient()

    prompt = build_architecture_prompt(components, relationships, context_groups)
    raw = llm.generate(prompt)

    return _parse_architecture_style(raw)


def _parse_architecture_style(text: str) -> str:
    cleaned = text.strip().lower()
    return cleaned.split()[0] if cleaned else "unknown"
