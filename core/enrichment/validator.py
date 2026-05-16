def validate_enrichment_input(payload: dict) -> tuple[dict | None, str | None]:
    if not isinstance(payload, dict):
        return None, "Payload must be a JSON object"

    if not isinstance(payload.get("components"), list):
        return None, "Field 'components' must be a list"

    if not isinstance(payload.get("relationships"), list):
        return None, "Field 'relationships' must be a list"

    return payload, None
