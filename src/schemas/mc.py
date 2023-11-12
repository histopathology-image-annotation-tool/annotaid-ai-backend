from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, NonNegativeFloat, field_validator

from src.schemas.nuclick import Keypoint
from src.utils.utils import read_file


class BoundingBox(BaseModel):
    """Represents a 2D bounding box."""
    x: NonNegativeFloat
    y: NonNegativeFloat
    width: NonNegativeFloat
    height: NonNegativeFloat


class MitosisLabel(str, Enum):
    """Represents possible labels for mitosis."""
    mitosis = 'mitosis'
    hard_negative_mitosis = 'hard_negative_mitosis'


class Mitosis(BaseModel):
    """Represents a detected mitosis."""
    bbox: BoundingBox
    confidence: NonNegativeFloat = Field(
        ge=0.0,
        le=1.0,
        description="Confidence of a predicted label",

    )
    label: MitosisLabel

    @field_validator('confidence', mode='before')
    @classmethod
    def confidence_validator(cls, value: float) -> float:
        return round(value, 3)


class MCPredictRequest(BaseModel):
    """Represents a request containing information about an image.
    The image must be at least 512x512px.
    """
    image: str = Field(
        default=...,
        description="A base64-encoded string representing an RGB image."
    )
    offset: Keypoint | None = Field(
        default=None,
        description="An optional keypoint representing the offset "
        "to be added to the keypoints in the response."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "image": read_file(Path('./src/examples/image_512.txt')),
                    "offset": {"x": 1000, "y": 1500}
                },
            ]
        }
    }


class MCPredictResponse(BaseModel):
    """Represents the response containing detected mitosis."""
    mitosis: list[Mitosis]
