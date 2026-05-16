import json


_VALID_ARCHITECTURE_STYLES = [
    "3-tier architecture",
    "microservices",
    "event-driven microservices",
    "event-driven architecture",
    "event-driven 3-tier architecture",
    "monolith",
    "unknown",
]


def build_refinement_prompt(output_model: dict) -> str:
    components = output_model.get("components", [])
    frozen_ids = [c["id"] for c in components]

    return f"""You are refining a structured architecture model produced by a rule-based pipeline.

Current model:
{json.dumps(output_model, indent=2)}

STRICT RULES — violations will cause this response to be discarded:
- Return EXACTLY {len(components)} components — no additions, no removals.
- Component IDs are frozen: {json.dumps(frozen_ids)}. Do NOT change any id value.
- You MAY improve: component name for clarity, type for accuracy, technology label for consistency, aliases list.
- You MAY refine relationship type, protocol, and description — but only using the existing from/to IDs.
- Do NOT add new relationships. Do NOT remove existing relationships.
- architecture_style MUST be one of: {json.dumps(_VALID_ARCHITECTURE_STYLES)}.
  If the current value already fits, keep it. If a more precise label applies, use it.
- communication_patterns should be a list of strings describing the patterns present.
- confidence should reflect how confident you are in the classification (0.0 to 1.0).
- uncertainties should list any ambiguous aspects (empty list if none).

Return ONLY valid JSON with this exact top-level structure — no markdown, no explanation:
{{
  "components": [...],
  "relationships": [...],
  "architecture_style": "...",
  "communication_patterns": ["..."],
  "confidence": 0.0,
  "uncertainties": ["..."]
}}"""


def build_descriptions_prompt(relationships: list, components: list) -> str:
    return f"""You are improving human-readable descriptions of architectural relationships.

Components (for context only — IDs and names are frozen, do not modify):
{json.dumps(components, indent=2)}

Relationships to improve (fields from, to, type, protocol are frozen — only improve description):
{json.dumps(relationships, indent=2)}

For each relationship write a single concise sentence that explains:
- what data or request is being transmitted
- in which direction
- why (what business purpose it serves)
Use the component names (not IDs) for readability.

Example: "HTTP Request" → "The Frontend sends HTTP requests to the API Gateway to retrieve user data."

Return ONLY a JSON array of exactly {len(relationships)} objects with the same structure as the input.
Do NOT change from, to, type, or protocol — only update description.
No markdown, no explanation."""
