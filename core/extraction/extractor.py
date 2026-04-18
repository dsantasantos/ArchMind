from typing import Any


def extract(filename: str) -> dict[str, Any]:
    # Future: integrate OCR / vision model to process real image bytes
    return {
        "source": filename,
        "raw_elements": ["api_gateway", "service_a", "service_b", "database"],
        "raw_text": "Mocked extraction output",
    }
