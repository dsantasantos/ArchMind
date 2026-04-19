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


def build_architecture_prompt(components: list, relationships: list) -> str:
    return f"""Given the components and relationships:

Components:
{components}

Relationships:
{relationships}

Identify the architecture style:
(layered, microservices, monolith)

Consider:
- Number of services
- Relationship patterns
- System structure

Rules:
- Return ONLY one word
- Do not explain"""


def build_relationships_prompt(components: list, data: dict) -> str:
    return f"""You are given:

Components:
{components}

Visual connections:
{data["visual_elements"]}

Infer relationships between components.

Also infer the type:
- http_request
- database_query
- internal_call

Rules:
- Use component IDs (c1, c2, etc.)
- Do not invent components
- Only create relationships that are supported by visual connections
- Infer the most appropriate type based on context

Return JSON:
[
  {{ "from": "c1", "to": "c2", "type": "..." }}
]

Return only the JSON array, no explanation."""
