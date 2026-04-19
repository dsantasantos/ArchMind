from typing import Any

from schemas.structuring_schema import StructuringInput
from core.structuring.component_recognizer import recognize_components
from core.structuring.relationship_recognizer import recognize_relationships


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
    components = recognize_components(data.text_blocks)
    visual_elements = [ve.model_dump(by_alias=True) for ve in data.visual_elements]
    relationships = recognize_relationships(components, visual_elements)
    return {
        "components": components,
        "relationships": relationships,
    }
