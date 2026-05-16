import logging

logger = logging.getLogger(__name__)


def infer_implicit_characteristics(
    components: list[dict],
    relationships: list[dict],
    execution_id: str,
) -> list[str]:
    backend_count = sum(1 for c in components if c.get("type") == "backend_service")
    frontend_count = sum(1 for c in components if c.get("type") == "frontend_application")
    db_count = sum(
        1 for c in components
        if c.get("type") in ("relational_database", "document_db")
        or c.get("technology_normalized") in ("relational_db", "document_db")
    )
    all_sync = all(r.get("synchrony") == "synchronous" for r in relationships) if relationships else False

    characteristics: list[str] = []

    if backend_count == 1:
        characteristics.append("centralized_backend")
    if frontend_count == 1:
        characteristics.append("single_point_of_entry")
    if db_count == 1:
        characteristics.append("single_database")
    if all_sync and relationships:
        characteristics.append("synchronous_flow_end_to_end")

    logger.info(
        "Implicit characteristics inferred",
        extra={
            "execution_id": execution_id,
            "step": "inference",
            "characteristics": characteristics,
            "backend_count": backend_count,
            "frontend_count": frontend_count,
            "db_count": db_count,
            "all_sync": all_sync,
        },
    )
    return characteristics
