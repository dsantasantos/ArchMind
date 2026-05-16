import logging

logger = logging.getLogger(__name__)

_TYPE_MAP = {
    "service": "backend_service",
    "database": "relational_database",
    "frontend": "frontend_application",
}

_TECH_NORMALIZATION: dict[str, str] = {
    "react": "frontend_framework",
    "angular": "frontend_framework",
    "vue": "frontend_framework",
    "svelte": "frontend_framework",
    "postgresql": "relational_db",
    "postgres": "relational_db",
    "mysql": "relational_db",
    "sqlite": "relational_db",
    "sql server": "relational_db",
    "oracle": "relational_db",
    "mongodb": "document_db",
    "redis": "cache_db",
    "kafka": "message_broker",
    "rabbitmq": "message_broker",
    "elasticsearch": "search_engine",
    "spring boot": "backend_framework",
    "node.js": "backend_framework",
    "nodejs": "backend_framework",
    ".net": "backend_framework",
    "django": "backend_framework",
    "flask": "backend_framework",
    "fastapi": "backend_framework",
    "express": "backend_framework",
    "rest api": "api_protocol",
    "graphql": "api_protocol",
    "grpc": "api_protocol",
    "soap": "api_protocol",
}


def normalize_components(components: list[dict], execution_id: str) -> list[dict]:
    type_mappings: dict[str, int] = {}
    tech_mappings: dict[str, int] = {}

    for comp in components:
        original_type = comp.get("type", "service")
        normalized_type = _TYPE_MAP.get(original_type, original_type)
        comp["type"] = normalized_type
        type_mappings[f"{original_type}->{normalized_type}"] = (
            type_mappings.get(f"{original_type}->{normalized_type}", 0) + 1
        )

        raw_tech = comp.get("technology", "")
        comp["raw_technology"] = raw_tech
        comp["technology_normalized"] = _normalize_technology(raw_tech)
        if raw_tech:
            tech_mappings[raw_tech] = tech_mappings.get(raw_tech, 0) + 1

    logger.info(
        "Normalization completed",
        extra={
            "execution_id": execution_id,
            "step": "normalization",
            "components_normalized": len(components),
            "type_mappings": type_mappings,
            "tech_mappings": tech_mappings,
        },
    )
    return components


def _normalize_technology(tech: str) -> str:
    if not tech:
        return "unknown"
    tech_lower = tech.lower()
    for key, normalized in _TECH_NORMALIZATION.items():
        if key in tech_lower:
            return normalized
    return "unknown"
