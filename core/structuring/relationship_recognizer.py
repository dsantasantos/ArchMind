from schemas.structuring_schema import StructuringInput

_TYPE_RULES: dict[str, list[str]] = {
    "synchronous_request": ["http request", "rest", "api call"],
    "database_query": ["database queries", "query"],
}

_PROTOCOL_RULES: dict[str, str] = {
    "HTTP": ["http"],
    "gRPC": ["grpc"],
}


def recognize_relationships(components: list[dict], data: StructuringInput) -> list[dict]:
    name_to_id = {c["name"].strip().lower(): c["id"] for c in components}

    relationships = []
    for hint in data.relationship_hints:
        from_id = name_to_id.get(hint.from_.strip().lower())
        to_id = name_to_id.get(hint.to.strip().lower())

        if from_id is None or to_id is None:
            continue

        relationships.append({
            "from": from_id,
            "to": to_id,
            "type": _normalize_type(hint.label),
            "protocol": _detect_protocol(hint.label),
            "description": hint.label,
        })

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
