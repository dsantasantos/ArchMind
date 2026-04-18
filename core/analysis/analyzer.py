from typing import Any


def analyze(structured_data: dict[str, Any]) -> dict[str, Any]:
    # Future: apply rule engines or LLM-backed reasoner to detect issues
    return {
        "step_count": structured_data.get("step_count", 0),
        "issues": [
            "Possível ausência de validação no passo 2",
            "Alto acoplamento entre serviços",
        ],
        "recommendations": [
            "Aplicar separação de responsabilidades",
            "Adicionar camada de validação",
        ],
    }
