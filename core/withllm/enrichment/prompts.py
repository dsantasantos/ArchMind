def build_enrichment_prompt(data: dict) -> str:
    return f"""You are an expert software architect AI.

Your task is to enrich a structured architecture model.

You MUST:
- Normalize naming
- Classify technologies
- Add semantic attributes
- Reduce ambiguity
- Infer implicit characteristics

You MUST NOT:
- Invent components
- Remove existing elements
- Break structure

---

INPUT DATA:
{data}

---

ENRICHMENT GOALS:

### Components:
Enhance each component with:
- tech_type
- execution_model (if applicable)
- layer (presentation, application, data)
- subtype (if applicable)

### Relationships:
Enhance each relationship with:
- interaction_style
- synchrony
- direction
- improved description

### Architecture:
Normalize architecture style naming

### Implicit Characteristics:
Infer high-level properties such as:
- centralized_backend
- single_database
- synchronous_flow

### Derived Properties:
Infer:
- coupling
- scalability
- resilience
- distribution

### Gaps:
Identify missing elements such as:
- authentication
- caching
- async communication

---

OUTPUT FORMAT (STRICT JSON):

Return ONLY:

{{
  "components": [...],
  "relationships": [...],
  "architecture_style": "...",
  "implicit_characteristics": [...],
  "derived_properties": {{
    "coupling": "...",
    "scalability": "...",
    "resilience": "...",
    "distribution": "..."
  }},
  "gaps": [...],
  "confidence": 0.0
}}

---

RULES:
- Do NOT explain
- Do NOT add markdown
- Do NOT add comments
- Return ONLY valid JSON
"""
