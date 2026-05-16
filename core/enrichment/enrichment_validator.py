import logging

logger = logging.getLogger(__name__)

_REQUIRED_COMPONENT_FIELDS = {"type", "layer", "tech_type"}
_REQUIRED_DERIVED_KEYS = {"coupling", "scalability", "resilience", "distribution"}


def validate_output(output: dict, execution_id: str) -> dict:
    inconsistencies: list[str] = []
    confidence = output.get("confidence", 1.0)

    components = output.get("components", [])
    relationships = output.get("relationships", [])
    derived = output.get("derived_properties", {})
    implicit = output.get("implicit_characteristics", [])

    comp_ids = {c.get("id") for c in components if c.get("id")}

    for comp in components:
        missing = _REQUIRED_COMPONENT_FIELDS - set(comp.keys())
        if missing:
            inconsistencies.append(
                f"Component '{comp.get('id', '?')}' missing fields: {missing}"
            )

    for rel in relationships:
        from_id = rel.get("from")
        to_id = rel.get("to")
        if from_id and from_id not in comp_ids:
            inconsistencies.append(f"Relationship references unknown source component: '{from_id}'")
        if to_id and to_id not in comp_ids:
            inconsistencies.append(f"Relationship references unknown target component: '{to_id}'")

    missing_derived = _REQUIRED_DERIVED_KEYS - set(derived.keys())
    if missing_derived:
        inconsistencies.append(f"derived_properties missing keys: {missing_derived}")

    if not isinstance(implicit, list):
        inconsistencies.append("implicit_characteristics must be a list")

    deduction = min(len(inconsistencies) * 0.05, 0.3)
    output["confidence"] = round(max(confidence - deduction, 0.0), 2)

    logger.info(
        "Output validation completed",
        extra={
            "execution_id": execution_id,
            "step": "validation",
            "inconsistencies_found": len(inconsistencies),
            "inconsistencies": inconsistencies,
            "confidence": output["confidence"],
        },
    )
    return output
