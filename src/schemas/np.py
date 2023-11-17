from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from src.utils.utils import read_file


class NPLabel(str, Enum):
    """Represents nuclear pleomorphism scores.
    The undetermined class is returned when the stain normalization process fails.
    """
    undetermined = 'undetermined'
    score_1 = 'score_1'
    score_2 = 'score_2'
    score_3 = 'score_3'


class NPPredictRequest(BaseModel):
    """Represents a request containing information abount an image.
    The image must be at least 256x256px from x20 magnification.
    """
    image: str = Field(
        default=...,
        description="A base64-encoded string representing an RGB image."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "image": read_file(Path('./src/examples/image_512.txt')),
                },
            ]
        }
    }


class NPPredictResponse(BaseModel):
    """Represents the response containing nuclear pleomorphism label."""
    label: NPLabel
