from schemas.structuring_schema import StructuringInput
from core.structuring.component_recognizer import recognize_components
from core.structuring.relationship_recognizer import recognize_relationships
from core.structuring.architecture_recognizer import recognize_architecture_style
from core.structuring.validator import validate_structural_integrity


def process(data: StructuringInput) -> dict:
    # 1. Identifica os componentes
    components = recognize_components(data)

    # 2. Mapeia relacionamentos entre esses componentes
    raw_relationships = recognize_relationships(components, data)

    # 3. Valida a integridade (Garante que relacionamentos apontam para componentes reais)
    relationships = validate_structural_integrity(components, raw_relationships)

    # 4. Infere o estilo arquitetural baseado nos dados limpos
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
