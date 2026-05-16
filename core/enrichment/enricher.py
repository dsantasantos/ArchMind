import logging
import uuid

from core.enrichment.normalizer import normalize_components
from core.enrichment.classifier import classify_components
from core.enrichment.relationship_enricher import enrich_relationships
from core.enrichment.inferencer import infer_implicit_characteristics
from core.enrichment.properties_deriver import derive_properties
from core.enrichment.gap_detector import detect_gaps
from core.enrichment.enrichment_validator import validate_output

logger = logging.getLogger(__name__)


def enrich(data: dict) -> dict:
    execution_id = str(uuid.uuid4())

    components = [c.copy() for c in data.get("components", [])]
    relationships = [r.copy() for r in data.get("relationships", [])]
    architecture_style = data.get("architecture_style", "")
    communication_patterns = data.get("communication_patterns", [])
    uncertainties = data.get("uncertainties", [])

    logger.info(
        "Enrichment pipeline started",
        extra={
            "execution_id": execution_id,
            "components_count": len(components),
            "relationships_count": len(relationships),
            "architecture_style": architecture_style,
        },
    )

    try:
        components = normalize_components(components, execution_id)
        components = classify_components(components, execution_id)
        relationships = enrich_relationships(relationships, components, execution_id)
        implicit_characteristics = infer_implicit_characteristics(components, relationships, execution_id)
        derived_properties = derive_properties(components, relationships, implicit_characteristics, execution_id)
        gaps = detect_gaps(components, relationships, execution_id)

        output = {
            "components": components,
            "relationships": relationships,
            "architecture_style": architecture_style,
            "communication_patterns": communication_patterns,
            "uncertainties": uncertainties,
            "implicit_characteristics": implicit_characteristics,
            "derived_properties": derived_properties,
            "gaps": gaps,
            "confidence": 1.0,
        }

        output = validate_output(output, execution_id)
        output["execution_id"] = execution_id

        logger.info(
            "Enrichment pipeline completed",
            extra={
                "execution_id": execution_id,
                "components_count": len(components),
                "relationships_count": len(relationships),
                "implicit_characteristics": implicit_characteristics,
                "gaps_count": len(gaps),
                "confidence": output["confidence"],
            },
        )

        return output

    except Exception as exc:
        logger.error(
            "Enrichment pipeline failed with unexpected error",
            extra={"execution_id": execution_id, "error": str(exc)},
        )
        raise
