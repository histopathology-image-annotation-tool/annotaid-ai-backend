from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, NonNegativeFloat

from src.utils.utils import read_file


class Keypoint(BaseModel):
    """Represents a 2D coordinate point."""
    x: NonNegativeFloat
    y: NonNegativeFloat


class NuclickPredictRequest(BaseModel):
    """Represents a request containing information about an image and user clicks.
    The image must be at least 128x128px.
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
    keypoints: list[Keypoint] = Field(
        default=...,
        min_length=1,
        max_length=16,
        description="A list of user-defined keypoints relative "
        "to the top left corner of the image."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "image": read_file(Path('./src/examples/image.txt')),
                    "offset": {"x": 1000, "y": 1500},
                    "keypoints": [
                        {"x": 177, "y": 42},
                        {"x": 135, "y": 78}
                    ]
                },
            ]
        }
    }


class NuclickPredictResponse(BaseModel):
    """Represents the response containing segmented nuclei data.
    Each inner list represents a set of keypoints outlining segmented nuclei
    in the processed image.
    """
    segmented_nuclei: list[list[Keypoint]]
