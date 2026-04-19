def build_prompt(data: dict) -> str:
    return f"""You are analyzing extracted text from an architecture diagram.

Text elements:
{data["text_blocks"]}

Identify architecture components only.

Ignore:
- Technical actions (e.g., "HTTP Request")
- Communication types (e.g., "REST API")
- Generic labels that are not components

Classify each component as one of:
- frontend
- service
- database

Rules:
- Return only relevant architecture components
- Do not duplicate components
- Normalize names if needed (e.g., "React Application" -> "Frontend")

Return JSON in the format:
[
  {{ "id": "c1", "name": "...", "type": "..." }}
]

Return only the JSON array, no explanation."""
