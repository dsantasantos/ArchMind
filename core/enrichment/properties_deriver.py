import logging

logger = logging.getLogger(__name__)


def derive_properties(
    components: list[dict],
    relationships: list[dict],
    implicit_characteristics: list[str],
    execution_id: str,
) -> dict:
    coupling = _derive_coupling(relationships)
    scalability = _derive_scalability(components, implicit_characteristics)
    resilience = _derive_resilience(components, relationships)
    distribution = _derive_distribution(components)

    properties = {
        "coupling": coupling,
        "scalability": scalability,
        "resilience": resilience,
        "distribution": distribution,
    }

    logger.info(
        "Derived properties computed",
        extra={
            "execution_id": execution_id,
            "step": "inference",
            "derived_properties": properties,
            "total_components": len(components),
            "total_relationships": len(relationships),
        },
    )
    return properties


def _derive_coupling(relationships: list[dict]) -> str:
    if not relationships:
        return "low"
    total = len(relationships)
    sync_count = sum(1 for r in relationships if r.get("synchrony") == "synchronous")
    ratio = sync_count / total
    if ratio > 0.7:
        return "high"
    if ratio > 0.3:
        return "medium"
    return "low"


def _derive_scalability(components: list[dict], implicit_characteristics: list[str]) -> str:
    if "single_database" in implicit_characteristics:
        return "limited"
    backend_count = sum(1 for c in components if c.get("type") == "backend_service")
    if backend_count <= 1:
        return "medium"
    return "high"


def _derive_resilience(components: list[dict], relationships: list[dict]) -> str:
    has_messaging = any(c.get("tech_type") == "messaging" for c in components)
    has_async = any(r.get("synchrony") == "asynchronous" for r in relationships)
    if has_messaging or has_async:
        return "medium"
    return "low"


def _derive_distribution(components: list[dict]) -> str:
    count = len(components)
    if count <= 2:
        return "low"
    if count <= 5:
        return "medium"
    return "high"
