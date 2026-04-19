from pydantic import BaseModel, Field
from typing import List


class VisualElement(BaseModel):
    model_config = {"populate_by_name": True}

    from_: str = Field(..., alias="from")
    to: str


class StructuringInput(BaseModel):
    text_blocks: List[str]
    visual_elements: List[VisualElement]
