import uuid
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from src.utils.utils import read_file

from .shared import BoundingBox, Keypoint


class SAMKeypointLabel(str, Enum):
    """Enumeration representing the label of the SAM keypoint.

    The `foreground` label indicates that the user wants to include the given location.
    The `background` label indicates that the user wants to exclude the given location.
    """
    foreground = 'foreground'
    background = 'background'


class SAMKeypoint(BaseModel):
    """Represents the SAM keypoint."""
    keypoint: Keypoint
    label: SAMKeypointLabel


class SAMPredictRequestPostprocessing(BaseModel):
    """Represents SAM model postprocessing parameters."""
    multimask_output: bool | None = Field(
        default=None,
        description="When True, SAM predicts 3 masks with confidence scores. "
        "The mask with highest confidence is selected for processing. "
        "Set to True if the single point is provided; False for multiple points. "
        "When null, parameter is set to False, if the bbox/multiple points is provided."
    )
    min_object_size: PositiveInt | None = Field(
        default=10,
        description="Remove objects smaller than specified size. "
        "See: https://scikit-image.org/docs/stable/api/skimage.morphology.html#"
        "skimage.morphology.remove_small_objects. "
        "When null, the operation is omitted."
    )
    remove_holes_smaller_than: PositiveInt | None = Field(
        default=30,
        description="Remove holes smaller than specified size. "
        "See: https://scikit-image.org/docs/stable/api/skimage.morphology.html#"
        "skimage.morphology.remove_small_holes. "
        "When null, the operation is omitted."
    )
    reconstruction: bool | None = Field(
        default=True,
        description="Perform morphological reconstruction of an image. "
        "See: https://scikit-image.org/docs/stable/api/skimage.morphology.html#"
        "skimage.morphology.reconstruction. "
        "When null, the operation is omitted."
    )


class SAMPredictRequest(BaseModel):
    """Represents a request for SAMPredict endpoint."""
    embeddings_task_id: uuid.UUID = Field(
        default=...,
        description="A task ID from the extract embeddings task for the given ROI."
    )
    previous_predict_task_id: uuid.UUID | None = Field(
        default=None,
        description="A task ID of the previous prediction. The low-resolution "
        "segmentation mask of the previous prediction is fed to the model to help "
        "refine the segmentation result."
    )
    offset: Keypoint | None = Field(
        default=None,
        description="An optional keypoint representing the offset to be added "
        "to the keypoints in the response."
    )
    bbox: BoundingBox | None = Field(
        default=None,
        description="Sub-ROI of the original extracted ROI to perform "
        "automatic segmentation. "
        "The segmented objects from this sub-ROI can be refined with keypoints."
    )
    keypoints: list[SAMKeypoint] | None = Field(
        default=None,
        min_length=1,
        max_length=16,
        description="Coordinates of the user clicks to indicate guidance signals "
        "for the segmentation. When refining the previous segmented objects, all used "
        "keypoints from the beginning of the segmentation process must be provided."
    )
    postprocessing: SAMPredictRequestPostprocessing | None = Field(
        default=SAMPredictRequestPostprocessing(),
        description="Mask postprocessing parameters. When the config is not provided "
        "the default config is used."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "openapi_examples": {
                "with_bbox": {
                    "summary": "Bounding boxes example",
                    "description": "An example with bounding boxes.",
                    "value": {
                        "embeddings_task_id": "565b71f0-3772-4241-9c28-5e3a4f6adbf3",
                        "bbox": {"x": 0, "y": 0, "width": 200, "height": 200}
                    }
                },
                "with_points": {
                    "summary": "Points example",
                    "description": "An example with user clicks.",
                    "value": {
                        "embeddings_task_id": "565b71f0-3772-4241-9c28-5e3a4f6adbf3",
                        "keypoints": [
                            {
                                "keypoint": {"x": 50, "y": 50},
                                "label": "foreground"
                            }
                        ]
                    }
                },
                "with_previous_predict_task": {
                    "summary": "Previous predict task example",
                    "description": "An example with a previous predict task where the "
                    "low-resolution segmentation mask is used to refine "
                    "segmented objects.",
                    "value": {
                        "embeddings_task_id": "565b71f0-3772-4241-9c28-5e3a4f6adbf3",
                        "previous_predict_task_id": "3930f751-a433-4232-8220-"
                        "5fae555d6de6",
                        "keypoints": [
                            {
                                "keypoint": {"x": 50, "y": 50},
                                "label": "foreground"
                            },
                            {
                                "keypoint": {"x": 100, "y": 100},
                                "label": "background"
                            }
                        ],
                        "offset": {"x": 1000, "y": 1500},
                    }
                }
            }
        }
    )


class SAMPredictResponse(BaseModel):
    """Represents the response containing segmented objects."""
    segmented_objects: list[list[Keypoint]]
    previous_predict_task_id: uuid.UUID


class GetSAMEmbeddingsRequest(BaseModel):
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
