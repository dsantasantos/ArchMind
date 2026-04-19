from typing import Any

from schemas.structuring_schema import StructuringInput
from core.structuring.component_recognizer import recognize_components


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


def process(data: StructuringInput) -> dict:
    return {
        "components": recognize_components(data.text_blocks),
    }
