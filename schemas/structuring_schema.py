from pydantic import BaseModel, Field
from typing import List


class GroupedElement(BaseModel):
    label: str
    texts: List[str]


class DetectedKeyword(BaseModel):
    text: str
    hint: str


class RelationshipHint(BaseModel):
    model_config = {"populate_by_name": True}

    from_: str = Field(..., alias="from")
    to: str
    label: str


class ContextGroup(BaseModel):
    name: str
    contains: List[str]


class StructuringInput(BaseModel):
    text_blocks: List[str]
    grouped_elements: List[GroupedElement]
    detected_keywords: List[DetectedKeyword]
    relationship_hints: List[RelationshipHint]
    context_groups: List[ContextGroup]
