from typing import Any
from schemas.report_schema import DiagramReport


def generate_report(filename: str, analysis_result: dict[str, Any]) -> DiagramReport:
    # Single assembly point: only this stage constructs the output schema
    step_count = analysis_result.get("step_count", 0)
    return DiagramReport(
        diagram_name=filename,
        summary=f"Fluxo identificado com {step_count} etapas principais",
        issues=analysis_result.get("issues", []),
        recommendations=analysis_result.get("recommendations", []),
    )
