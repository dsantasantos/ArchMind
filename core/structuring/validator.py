from pydantic import ValidationError

from schemas.structuring_schema import StructuringInput


def validate_structuring_input(data: dict) -> tuple[StructuringInput | None, str | None]:
    try:
        return StructuringInput.model_validate(data), None
    except ValidationError:
        return None, "Invalid payload structure"
