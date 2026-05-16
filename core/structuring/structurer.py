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
from core.structuring.architecture_recognizer import recognize_architecture_style
from core.structuring.communication_pattern_recognizer import recognize_communication_patterns


def process(data: StructuringInput) -> dict:
    components = recognize_components(data)
    relationships = recognize_relationships(components, data)
    context_groups = [g.model_dump() for g in data.context_groups]
    arch_result = recognize_architecture_style(components, relationships, context_groups)

    output_model = {
        "components": components,
        "relationships": relationships,
        "architecture_style": arch_result.get("architecture_style", "unknown"),
        "communication_patterns": [],
        "confidence": arch_result.get("confidence", 0.0),
        "uncertainties": arch_result.get("uncertainties", []),
    }

    recognize_communication_patterns(relationships, output_model)
    return output_model
