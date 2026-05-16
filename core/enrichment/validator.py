def validate_enrichment_input(payload: dict) -> tuple[dict | None, str | None]:
    if not isinstance(payload, dict):
        return None, "Payload must be a JSON object"

    if payload.get("status") == "success" and "data" in payload:
        inner = payload["data"]
        if not isinstance(inner, dict):
            return None, "Field 'data' must be a JSON object"
        if not isinstance(inner.get("components"), list):
            return None, "Field 'data.components' must be a list"
        if not isinstance(inner.get("relationships"), list):
            return None, "Field 'data.relationships' must be a list"
        return inner, None

    if not isinstance(payload.get("components"), list):
        return None, "Field 'components' must be a list"
    if not isinstance(payload.get("relationships"), list):
        return None, "Field 'relationships' must be a list"

    return payload, None
