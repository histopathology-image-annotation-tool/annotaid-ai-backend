from pathlib import Path

from pydantic import BaseModel, Field

from src.utils.utils import read_file

from .shared import BoundingBox, Keypoint


class SAMPredictRequest(BaseModel):
    image: str = Field(
        default=...,
        description="A base64-encoded string representing an RGB image."
    )
    bboxes: list[BoundingBox]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "image": read_file(Path('./src/examples/image_512.txt')),
                    "bboxes": [{"x": 0, "y": 0, "width": 200, "height": 200}]
                },
            ]
        }
    }


class SAMPredictResponse(BaseModel):
    segmented_object: list[Keypoint]
