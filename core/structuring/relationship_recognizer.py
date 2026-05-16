import logging

from schemas.structuring_schema import StructuringInput

logger = logging.getLogger(__name__)

_TYPE_RULES: dict[str, list[str]] = {
    "synchronous_request": ["http request", "rest", "api call"],
    "database_query": ["database queries", "query"],
}

_PROTOCOL_RULES: dict[str, str] = {
    "HTTP": ["http"],
    "gRPC": ["grpc"],
}


def recognize_relationships(components: list[dict], data: StructuringInput, execution_id: str) -> list[dict]:
    name_to_id = {c["name"].strip().lower(): c["id"] for c in components}

    relationships = []
    for hint in data.relationship_hints:
        from_id = name_to_id.get(hint.from_.strip().lower())
        to_id = name_to_id.get(hint.to.strip().lower())

        if from_id is None or to_id is None:
            logger.warning(
                "Relationship hint skipped — endpoint not found in known components",
                extra={
                    "execution_id": execution_id,
                    "from": hint.from_,
                    "to": hint.to,
                    "label": hint.label,
                },
            )
            continue

        relationships.append({
            "from": from_id,
            "to": to_id,
            "type": _normalize_type(hint.label),
            "protocol": _detect_protocol(hint.label),
            "description": hint.label,
        })

    logger.info(
        "Relationships normalized",
        extra={
            "execution_id": execution_id,
            "resolved_count": len(relationships),
            "skipped_count": len(data.relationship_hints) - len(relationships),
        },
    )
    return relationships


def _normalize_type(label: str) -> str:
    normalized = label.strip().lower()
    for rel_type, keywords in _TYPE_RULES.items():
        if any(kw in normalized for kw in keywords):
            return rel_type
    return "unknown"


def _detect_protocol(label: str) -> str | None:
    normalized = label.strip().lower()
    for protocol, keywords in _PROTOCOL_RULES.items():
        if any(kw in normalized for kw in keywords):
            return protocol
    return None
