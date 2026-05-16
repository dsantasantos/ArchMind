from schemas.structuring_schema import StructuringInput
from core.withllm.structuring.component_recognizer import recognize_components
from core.withllm.structuring.relationship_recognizer import recognize_relationships
from core.withllm.structuring.architecture_recognizer import recognize_architecture_style


def process(data: StructuringInput) -> dict:
    components = recognize_components(data)
    relationships = recognize_relationships(components, data)
    context_groups = [g.model_dump() for g in data.context_groups]
    arch_result = recognize_architecture_style(components, relationships, context_groups)
    return {
        "components": components,
        "relationships": relationships,
        "architecture_style": arch_result.get("architecture_style", "unknown"),
        "communication_patterns": arch_result.get("communication_patterns", []),
        "confidence": arch_result.get("confidence", 0.0),
        "uncertainties": arch_result.get("uncertainties", []),
    }
