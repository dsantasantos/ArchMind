import logging

logger = logging.getLogger(__name__)

_TECH_TYPE_MAP: dict[str, str] = {
    "frontend_framework": "ui",
    "relational_db": "storage",
    "document_db": "storage",
    "cache_db": "storage",
    "message_broker": "messaging",
    "search_engine": "storage",
    "backend_framework": "application",
    "api_protocol": "application",
}

_LAYER_MAP: dict[str, str] = {
    "frontend_application": "presentation",
    "backend_service": "application",
    "relational_database": "data",
    "message_broker": "integration",
}

_SUBTYPE_MAP: dict[str, str] = {
    "relational_db": "relational",
    "document_db": "document",
    "cache_db": "cache",
    "message_broker": "async",
    "frontend_framework": "spa",
    "backend_framework": "web",
    "api_protocol": "api",
}


def classify_components(components: list[dict], execution_id: str) -> list[dict]:
    layer_distribution: dict[str, int] = {}
    tech_type_distribution: dict[str, int] = {}

    for comp in components:
        tech_norm = comp.get("technology_normalized", "unknown")
        comp_type = comp.get("type", "")

        tech_type = _TECH_TYPE_MAP.get(tech_norm, "unknown")
        comp["tech_type"] = tech_type

        layer = _LAYER_MAP.get(comp_type, "application")
        comp["layer"] = layer

        subtype = _SUBTYPE_MAP.get(tech_norm)
        if subtype:
            comp["subtype"] = subtype

        layer_distribution[layer] = layer_distribution.get(layer, 0) + 1
        tech_type_distribution[tech_type] = tech_type_distribution.get(tech_type, 0) + 1

    logger.info(
        "Classification completed",
        extra={
            "execution_id": execution_id,
            "step": "classification",
            "components_classified": len(components),
            "layer_distribution": layer_distribution,
            "tech_type_distribution": tech_type_distribution,
        },
    )
    return components
