def build_components_prompt(data: dict) -> str:
    return f"""You are analyzing structured data extracted from an architecture diagram.

Text elements:
{data["text_blocks"]}

Pre-grouped elements (visual proximity groups from the diagram):
{data["grouped_elements"]}

Detected keyword hints (semantic classification clues):
{data["detected_keywords"]}

Contextual layers:
{data["context_groups"]}

Identify architecture components only.

Use the provided context to improve accuracy:
- Use detected_keywords hints to classify component types (e.g., hint "database_system" -> type "database")
- Use grouped_elements to merge closely related texts into a single component
- Use context_groups layer names to understand each component's architecture layer
- Ignore communication types and protocols (e.g., "HTTP Request", "REST API", "Database Queries") — these are relationships, not components

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


def build_relationships_prompt(components: list, data: dict) -> str:
    return f"""You are given:

Components:
{components}

Relationship hints (from/to pairs with connection labels):
{data["relationship_hints"]}

Detected keyword hints (for protocol/communication context):
{data["detected_keywords"]}

Infer relationships between components.

Use the label in each relationship hint to determine the relationship type:
- Labels containing HTTP, REST, request -> http_request
- Labels containing database, query, SQL -> database_query
- Other internal connections -> internal_call

Rules:
- Use component IDs (c1, c2, etc.)
- Do not invent components
- Only create relationships supported by the relationship hints
- Infer the most appropriate type from the label

Return JSON:
[
  {{ "from": "c1", "to": "c2", "type": "..." }}
]

Return only the JSON array, no explanation."""


def build_architecture_prompt(components: list, relationships: list, context_groups: list = None) -> str:
    context_section = ""
    if context_groups:
        context_section = f"""
Contextual layer groups:
{context_groups}
"""
    return f"""Given the components and relationships:

Components:
{components}

Relationships:
{relationships}
{context_section}
Identify the architecture style:
(layered, microservices, monolith)

Consider:
- Layer names in context_groups (e.g., "Frontend Layer", "API Layer", "Data Layer" strongly suggests layered)
- Number of services
- Relationship patterns
- System structure

Rules:
- Return ONLY one word
- Do not explain"""
