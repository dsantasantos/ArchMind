from typing import Any


def structure(raw_data: dict[str, Any]) -> dict[str, Any]:
    # Future: map OCR tokens to component/relationship entities via LLM
    elements = raw_data.get("raw_elements", [])
    return {
        "components": elements,
        "relationships": [
            {"from": "api_gateway", "to": "service_a"},
            {"from": "service_a", "to": "database"},
        ],
        "step_count": len(elements),
    }
