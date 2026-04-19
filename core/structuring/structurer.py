from typing import Any

from schemas.structuring_schema import StructuringInput
from core.structuring.component_recognizer import recognize_components
from core.structuring.relationship_recognizer import recognize_relationships
from core.structuring.architecture_recognizer import recognize_architecture_style


def structure(raw_data: dict[str, Any]) -> dict[str, Any]:
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
    architecture_style = recognize_architecture_style(components, relationships)
    return {
        "components": components,
        "relationships": relationships,
        "architecture_style": architecture_style,
    }
