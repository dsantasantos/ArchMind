import logging
from collections import Counter

logger = logging.getLogger(__name__)

VALID_COMPONENT_TYPES = {"frontend", "database", "service"}
VALID_RELATIONSHIP_TYPES = {
    "synchronous_request",
    "database_query",
    "database_response",
    "internal_call",
    "async_message",
}


class StructuringValidationError(Exception):
    pass


def validate_output_structure(output_model: dict, execution_id: str) -> None:
    errors: list[str] = []

    if "architecture_style" not in output_model:
        errors.append("Missing required field: 'architecture_style'")

    for i, comp in enumerate(output_model.get("components", [])):
        for field in ("id", "name", "type"):
            if not comp.get(field):
                errors.append(f"Component[{i}] missing required field: '{field}'")

    for i, rel in enumerate(output_model.get("relationships", [])):
        for field in ("from", "to", "type"):
            if not rel.get(field):
                errors.append(f"Relationship[{i}] missing required field: '{field}'")

    if errors:
        msg = f"Output structure validation failed: {'; '.join(errors)}"
        logger.error(msg, extra={"execution_id": execution_id, "errors": errors})
        raise StructuringValidationError(msg)


def detect_inconsistencies(output_model: dict) -> list[str]:
    components = output_model.get("components", [])
    relationships = output_model.get("relationships", [])

    issues: list[str] = []
    valid_ids = {c["id"] for c in components if c.get("id")}

    id_counts = Counter(c["id"] for c in components if c.get("id"))
    for comp_id, count in id_counts.items():
        if count > 1:
            issues.append(f"Duplicate component id: '{comp_id}'")

    name_counts = Counter(c["name"].strip().lower() for c in components if c.get("name"))
    for name, count in name_counts.items():
        if count > 1:
            issues.append(f"Duplicate component name: '{name}'")

    for comp in components:
        comp_type = comp.get("type", "")
        if comp_type not in VALID_COMPONENT_TYPES:
            issues.append(
                f"Component '{comp.get('name', comp.get('id', '?'))}' has invalid type: '{comp_type}'"
            )

    for rel in relationships:
        from_id = rel.get("from", "")
        to_id = rel.get("to", "")
        rel_type = rel.get("type", "")

        if from_id and from_id not in valid_ids:
            issues.append(f"Relationship references unknown component id: '{from_id}'")
        if to_id and to_id not in valid_ids:
            issues.append(f"Relationship references unknown component id: '{to_id}'")

        if rel_type not in VALID_RELATIONSHIP_TYPES:
            issues.append(
                f"Relationship between '{from_id}' and '{to_id}' has invalid type: '{rel_type}'"
            )

    return issues


def calculate_confidence(output_model: dict, inconsistencies: list[str]) -> float:
    components = output_model.get("components", [])
    relationships = output_model.get("relationships", [])
    architecture_style = output_model.get("architecture_style")

    score = 1.0

    unknown_components = sum(
        1 for c in components if c.get("type") not in VALID_COMPONENT_TYPES
    )
    score -= 0.2 * unknown_components

    unknown_relationships = sum(
        1 for r in relationships if r.get("type") not in VALID_RELATIONSHIP_TYPES
    )
    score -= 0.2 * unknown_relationships

    if not architecture_style or architecture_style == "unknown":
        score -= 0.1

    if inconsistencies:
        score -= 0.1

    return round(max(0.0, min(1.0, score)), 10)


def generate_uncertainties(output_model: dict, inconsistencies: list[str]) -> list[str]:
    components = output_model.get("components", [])
    relationships = output_model.get("relationships", [])

    uncertainties: list[str] = []

    for comp in components:
        comp_type = comp.get("type", "")
        if comp_type not in VALID_COMPONENT_TYPES:
            name = comp.get("name", comp.get("id", "?"))
            uncertainties.append(
                f"Component '{name}' could not be classified (type: '{comp_type}')"
            )

    for rel in relationships:
        rel_type = rel.get("type", "")
        if rel_type not in VALID_RELATIONSHIP_TYPES:
            from_id = rel.get("from", "?")
            to_id = rel.get("to", "?")
            if rel_type == "unknown":
                uncertainties.append(
                    f"Relationship between {from_id} and {to_id} has unknown type"
                )
            else:
                uncertainties.append(
                    f"Relationship between {from_id} and {to_id} has unrecognized type: '{rel_type}'"
                )

    # Add structural inconsistencies that are not already covered by type checks above
    type_issue_prefixes = (
        "Duplicate component",
        "Relationship references unknown component",
    )
    for issue in inconsistencies:
        if any(issue.startswith(prefix) for prefix in type_issue_prefixes):
            uncertainties.append(issue)

    return uncertainties


def validate_and_finalize(output_model: dict, execution_id: str) -> dict:
    validate_output_structure(output_model, execution_id)

    inconsistencies = detect_inconsistencies(output_model)
    output_model["confidence"] = calculate_confidence(output_model, inconsistencies)
    output_model["uncertainties"] = generate_uncertainties(output_model, inconsistencies)

    logger.info(
        "Output validation completed",
        extra={
            "execution_id": execution_id,
            "confidence": output_model["confidence"],
            "uncertainties_count": len(output_model["uncertainties"]),
            "inconsistencies_count": len(inconsistencies),
        },
    )

    return output_model
