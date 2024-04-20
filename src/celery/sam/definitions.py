import hashlib
from typing import Any, TypedDict

import numpy as np
import torch
from segment_anything import sam_model_registry
from segment_anything.build_sam import Sam

from celery import Task
from src.core.config import settings
from src.schemas.shared import Keypoint


class SamPredictorConfig(TypedDict):
    """The configuration for the SAM predictor."""
    original_size: tuple[int, ...]
    input_size: tuple[int, ...]
    features: np.ndarray
    is_image_set: bool


class SamPredictTaskResult(TypedDict):
    """The result of the SAM prediction task."""
    segmented_objects: list[list[Keypoint]]
    low_res_mask: np.ndarray


class SAMTask(Task):
    """The task for the SAM prediction pipeline."""
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: Sam = None
        self.model_hash: str | None = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            model = sam_model_registry[
                settings.SAM_MODEL_VARIANT
            ](settings.SAM_MODEL_PATH)
            model.to(self.device)

            self.model = model

            with open(settings.SAM_MODEL_PATH, 'rb') as model_file:
                self.model_hash = hashlib.md5(model_file.read()).hexdigest()

        return self.run(*args, **kwargs)
