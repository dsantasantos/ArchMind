from pydantic import BaseModel, Field
from typing import List


class DiagramReport(BaseModel):
    diagram_name: str = Field(..., description="Name of the uploaded diagram file")
    summary: str = Field(..., description="High-level summary of the identified flow")
    issues: List[str] = Field(default_factory=list, description="List of detected issues")
    recommendations: List[str] = Field(
        default_factory=list, description="List of architectural recommendations"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "diagram_name": "example.png",
                "summary": "Fluxo identificado com 3 etapas principais",
                "issues": [
                    "Possível ausência de validação no passo 2",
                    "Alto acoplamento entre serviços",
                ],
                "recommendations": [
                    "Aplicar separação de responsabilidades",
                    "Adicionar camada de validação",
                ],
            }
        }
    }
