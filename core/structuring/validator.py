from pydantic import ValidationError

from schemas.structuring_schema import StructuringInput


def validate_structuring_input(data: dict) -> tuple[StructuringInput | None, str | None]:
    try:
        return StructuringInput.model_validate(data), None
    except ValidationError:
        return None, "Invalid payload structure"


def validate_structural_integrity(components: list[dict], relationships: list[dict]) -> list[dict]:
    """
    Garante que todos os relacionamentos referenciem IDs de componentes válidos.
    Remove relacionamentos órfãos.
    """
    valid_ids = {c["id"] for c in components}
    valid_relationships = []

    for rel in relationships:
        if rel["from"] in valid_ids and rel["to"] in valid_ids:
            valid_relationships.append(rel)
        else:
            # Aqui poderíamos logar que um relacionamento foi descartado por falta de integridade
            pass

    return valid_relationships
