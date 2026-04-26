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
- Use detected_keywords hints to classify component types (e.g., hint "database_system" -> type "database", hint "frontend_framework" -> type "frontend")
- Use detected_keywords hints to determine the technology (e.g., "React Application" -> technology "React", "SQL Server" -> technology "SQL Server")
- Use grouped_elements to merge closely related texts into a single component and populate aliases
- Use context_groups layer names to understand each component's architecture layer
- Ignore communication types and protocols (e.g., "HTTP Request", "REST API", "Database Queries") — these are relationships, not components

Classify each component as one of:
- frontend
- service
- database

Rules:
- Return only relevant architecture components
- Do not duplicate components
- Normalize names if needed (e.g., "React Application" -> name "Frontend")
- technology: the specific technology/framework identified (e.g., "React", "SQL Server", "Spring Boot")
- aliases: other names this component appears as in the diagram (omit if none)

Return JSON in the format:
[
  {{ "id": "c1", "name": "...", "type": "...", "technology": "...", "aliases": ["..."] }}
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

Use the label in each relationship hint to determine:
- type: the nature of the interaction
  - synchronous_request: client-server HTTP/REST calls
  - database_query: write/read operations sent to a database
  - database_response: results returned from a database
  - internal_call: in-process or service-to-service call
  - async_message: asynchronous/queue-based communication
- protocol: the communication protocol if identifiable (e.g., "HTTP", "HTTPS", "AMQP", "gRPC") — omit if not determinable
- description: one sentence describing what this connection does

Rules:
- Use component IDs (c1, c2, etc.)
- Do not invent components
- Only create relationships supported by the relationship hints
- Infer direction: if A calls B, also add B's response to A when clearly implied

Return JSON:
[
  {{ "from": "c1", "to": "c2", "type": "...", "protocol": "...", "description": "..." }}
]

Return only the JSON array, no explanation."""


def build_architecture_prompt(components: list, relationships: list, context_groups: list = None) -> str:
    context_section = ""
    if context_groups:
        context_section = f"""
Contextual layer groups:
{context_groups}
"""
    return f"""Given the components and relationships of an architecture diagram:

Components:
{components}

Relationships:
{relationships}
{context_section}
Analyze the architecture and return a JSON object with the following fields:

- architecture_style: a concise human-readable name for the overall style (e.g., "3-tier architecture", "microservices", "monolith", "event-driven")
- communication_patterns: list of communication patterns present (e.g., "request-response", "synchronous communication", "async messaging")
- confidence: a float between 0 and 1 indicating how confident you are in this classification
- uncertainties: list of strings describing aspects that are ambiguous or unclear (empty list if none)

Consider:
- Layer names in context_groups (e.g., "Frontend Layer", "API Layer", "Data Layer" strongly suggests 3-tier)
- Number and types of services
- Relationship types and patterns

Return only a JSON object, no explanation:
{{
  "architecture_style": "...",
  "communication_patterns": ["..."],
  "confidence": 0.0,
  "uncertainties": ["..."]
}}"""
