from typing import Any

from schemas.structuring_schema import StructuringInput


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

from core.structuring.component_recognizer import recognize_components
from core.structuring.relationship_recognizer import recognize_relationships
from core.structuring.communication_pattern_recognizer import recognize_communication_patterns
from core.structuring.architecture_style_inferrer import infer_architecture_style


def process(data: StructuringInput) -> dict:
    components = recognize_components(data)
    relationships = recognize_relationships(components, data)

    output_model = {
        "components": components,
        "relationships": relationships,
        "architecture_style": None,
        "communication_patterns": [],
        "confidence": 1.0,
        "uncertainties": [],
    }

    recognize_communication_patterns(relationships, output_model)
    infer_architecture_style(components, output_model)
    return output_model
