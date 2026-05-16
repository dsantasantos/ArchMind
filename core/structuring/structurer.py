import logging
import uuid
from typing import Any

from schemas.structuring_schema import StructuringInput
from core.structuring.component_recognizer import recognize_components
from core.structuring.relationship_recognizer import recognize_relationships
from core.structuring.communication_pattern_recognizer import recognize_communication_patterns
from core.structuring.architecture_style_inferrer import infer_architecture_style
from core.structuring.llm_refiner import refine_with_llm, enrich_descriptions

logger = logging.getLogger(__name__)


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
    execution_id = str(uuid.uuid4())

    logger.info(
        "Structuring pipeline started",
        extra={
            "execution_id": execution_id,
            "grouped_elements_count": len(data.grouped_elements),
            "relationship_hints_count": len(data.relationship_hints),
            "detected_keywords_count": len(data.detected_keywords),
        },
    )

    try:
        components = recognize_components(data, execution_id)
        relationships = recognize_relationships(components, data, execution_id)

        output_model = {
            "components": components,
            "relationships": relationships,
            "architecture_style": None,
            "communication_patterns": [],
            "confidence": 1.0,
            "uncertainties": [],
        }

        recognize_communication_patterns(relationships, output_model, execution_id)
        infer_architecture_style(components, output_model, execution_id)

        output_model = refine_with_llm(output_model, execution_id)
        output_model = enrich_descriptions(output_model, execution_id)

        output_model["execution_id"] = execution_id

        logger.info(
            "Structuring pipeline completed",
            extra={
                "execution_id": execution_id,
                "components_count": len(components),
                "relationships_count": len(relationships),
                "architecture_style": output_model["architecture_style"],
                "communication_patterns": output_model["communication_patterns"],
            },
        )

        return output_model

    except Exception as exc:
        logger.error(
            "Structuring pipeline failed with unexpected error",
            extra={"execution_id": execution_id, "error": str(exc)},
        )
        raise
