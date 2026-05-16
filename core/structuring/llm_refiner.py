import json
import logging
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, ValidationError

from infra.llm.claude_client import ClaudeClient
from core.structuring.refiner_prompts import build_refinement_prompt, build_descriptions_prompt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic models — extra="ignore" strips unexpected LLM fields automatically
# ---------------------------------------------------------------------------

class RefinedComponent(BaseModel):
    model_config = {"extra": "ignore"}

    id: str
    name: str
    type: Literal["frontend", "service", "database"]
    technology: str = ""
    aliases: list[str] = Field(default_factory=list)


class RefinedRelationship(BaseModel):
    model_config = {"extra": "ignore", "populate_by_name": True}

    from_: str = Field(..., alias="from")
    to: str
    type: str
    protocol: Optional[str] = None
    description: str = ""


class RefinedOutputModel(BaseModel):
    model_config = {"extra": "ignore"}

    components: list[RefinedComponent]
    relationships: list[RefinedRelationship]
    architecture_style: Optional[str] = None
    communication_patterns: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    uncertainties: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_object(raw: str, execution_id: str, context: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning(
        "LLM refinement skipped — response is not valid JSON",
        extra={
            "execution_id": execution_id,
            "context": context,
            "reason": "json_decode_error",
            "raw_preview": raw[:200],
        },
    )
    return None


def _parse_json_array(raw: str, execution_id: str, context: str) -> list | None:
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    logger.warning(
        "Description enrichment skipped — response is not a JSON array",
        extra={
            "execution_id": execution_id,
            "context": context,
            "reason": "json_decode_error",
            "raw_preview": raw[:200],
        },
    )
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_llm_output(llm_response: str, original_model: dict, execution_id: str) -> dict:
    parsed = _parse_json_object(llm_response, execution_id, context="refinement")
    if parsed is None:
        return original_model

    try:
        refined = RefinedOutputModel.model_validate(parsed)
    except ValidationError as exc:
        logger.warning(
            "LLM refinement skipped — Pydantic validation failed",
            extra={
                "execution_id": execution_id,
                "reason": "pydantic_validation_error",
                "errors": exc.error_count(),
            },
        )
        return original_model

    original_ids = {c["id"] for c in original_model["components"]}
    refined_ids = {c.id for c in refined.components}
    if original_ids != refined_ids:
        logger.warning(
            "LLM refinement skipped — component IDs mutated",
            extra={
                "execution_id": execution_id,
                "reason": "id_integrity_violation",
                "expected_ids": sorted(original_ids),
                "received_ids": sorted(refined_ids),
            },
        )
        return original_model

    result = refined.model_dump(by_alias=True)
    if "execution_id" in original_model:
        result["execution_id"] = original_model["execution_id"]
    return result


def refine_with_llm(output_model: dict, execution_id: str) -> dict:
    logger.info(
        "LLM refinement started",
        extra={
            "execution_id": execution_id,
            "components_count": len(output_model.get("components", [])),
            "relationships_count": len(output_model.get("relationships", [])),
            "architecture_style_before": output_model.get("architecture_style"),
        },
    )

    llm = ClaudeClient()
    prompt = build_refinement_prompt(output_model)

    try:
        raw = llm.generate(prompt)
    except Exception as exc:
        logger.error(
            "LLM refinement call failed",
            extra={"execution_id": execution_id, "error": str(exc)},
        )
        return output_model

    result = validate_llm_output(raw, output_model, execution_id)

    logger.info(
        "LLM refinement completed",
        extra={
            "execution_id": execution_id,
            "architecture_style_after": result.get("architecture_style"),
            "refined": result is not output_model,
        },
    )
    return result


def enrich_descriptions(output_model: dict, execution_id: str) -> dict:
    relationships = output_model.get("relationships", [])

    if not relationships:
        logger.info(
            "Description enrichment skipped — no relationships",
            extra={"execution_id": execution_id},
        )
        return output_model

    logger.info(
        "Relationship description enrichment started",
        extra={
            "execution_id": execution_id,
            "relationships_count": len(relationships),
        },
    )

    llm = ClaudeClient()
    prompt = build_descriptions_prompt(relationships, output_model.get("components", []))

    try:
        raw = llm.generate(prompt)
    except Exception as exc:
        logger.error(
            "Description enrichment LLM call failed",
            extra={"execution_id": execution_id, "error": str(exc)},
        )
        return output_model

    parsed = _parse_json_array(raw, execution_id, context="description_enrichment")
    if parsed is None:
        return output_model

    if len(parsed) != len(relationships):
        logger.warning(
            "Description enrichment skipped — relationship count mismatch",
            extra={
                "execution_id": execution_id,
                "expected_count": len(relationships),
                "received_count": len(parsed),
            },
        )
        return output_model

    enriched = []
    fallback_count = 0
    for original, candidate in zip(relationships, parsed):
        try:
            validated = RefinedRelationship.model_validate(candidate)
            item = validated.model_dump(by_alias=True)
            # Enforce frozen structural fields regardless of what the LLM returned
            item["from"] = original["from"]
            item["to"] = original["to"]
            item["type"] = original["type"]
            item["protocol"] = original.get("protocol")
            enriched.append(item)
        except ValidationError:
            enriched.append(original)
            fallback_count += 1

    logger.info(
        "Relationship description enrichment completed",
        extra={
            "execution_id": execution_id,
            "enriched_count": len(enriched) - fallback_count,
            "fallback_count": fallback_count,
        },
    )

    return {**output_model, "relationships": enriched}
