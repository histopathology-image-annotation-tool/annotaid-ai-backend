from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torchvision
from celery import Celery, Task
from imantics import Mask
from torchvision.models import EfficientNet
from ultralytics import YOLO

from src.core.config import settings
from src.models import (
    NuClick_NN,
    predict_mc_first_stage,
    predict_mc_second_stage,
    predict_nuclick,
)
from src.models.mc.custom_types import MitosisPrediction
from src.schemas.nuclick import Keypoint

celery_app = Celery(
    __name__,
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_BACKEND_URL)
)
celery_app.conf.event_serializer = 'pickle'
celery_app.conf.task_serializer = 'pickle'
celery_app.conf.result_serializer = 'pickle'
celery_app.conf.accept_content = ['application/json', 'application/x-python-serialize']


class NuclickTask(Task):
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: NuClick_NN = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            model = NuClick_NN(n_channels=5, n_classes=1)

            model.to(self.device)

            model_state = torch.load(
                settings.NUCLICK_MODEL_PATH,
                map_location=self.device
            )
            model.load_state_dict(model_state)

            self.model = model

        return self.run(*args, **kwargs)


class MCFirstStageTask(Task):
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: YOLO = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            self.model = YOLO(settings.MC_FIRST_STAGE_MODEL_PATH, task='detect')

        return self.run(*args, **kwargs)


class MCSecondStageTask(Task):
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: EfficientNet = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            checkpoint = torch.load(
                settings.MC_SECOND_STAGE_MODEL_PATH,
                map_location='cpu'
            )

            model = torchvision.models.efficientnet_b2(weights=None)
            model.classifier = nn.Linear(in_features=1408, out_features=2)

            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)

            self.model = model

        return self.run(*args, **kwargs)


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=NuclickTask
)
def predict_nuclick_task(
    self: NuclickTask,
    image: np.ndarray,
    keypoints: list[Keypoint],
    offset: tuple[int, int]
) -> list[list[Keypoint]]:
    self.model.eval()

    result = predict_nuclick(
        model=self.model,
        image=image,
        keypoints=keypoints,
        device=self.device
    )

    polygons = Mask(result).polygons()

    return [
        [
            {
                "x": point[0] + offset[0],
                "y": point[1] + offset[1]
            }
            for point in nuclei_points
        ]
        for nuclei_points in polygons.points
    ]


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=MCFirstStageTask
)
def predict_mc_first_stage_task(
    self: MCFirstStageTask,
    image: np.ndarray
) -> list[np.ndarray]:
    return predict_mc_first_stage(
        model=self.model,
        image=image
    )


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=MCSecondStageTask
)
def predict_mc_second_stage_task(
    self: MCSecondStageTask,
    bboxes: list[np.ndarray],
    image: np.ndarray,
) -> list[MitosisPrediction]:
    return predict_mc_second_stage(
        model=self.model,
        image=image,
        bboxes=bboxes,
        device=self.device
    )


@celery_app.task(ignore_result=False)
def apply_offset_to_bboxes(
    mitosis_predictions: list[MitosisPrediction],
    offset: tuple[int, int]
) -> list[MitosisPrediction]:
    bbox_offset = np.array([*offset, *offset], dtype=np.int32)

    for result in mitosis_predictions:
        result['bbox'] += bbox_offset
        print(result['bbox'])

    return mitosis_predictions


@celery_app.task(ignore_result=False)
def predict_mc_task(
    image: np.ndarray,
    offset: tuple[int, int]
) -> list[MitosisPrediction]:
    chain = predict_mc_first_stage_task.s(image=image) | \
        predict_mc_second_stage_task.s(image=image) | \
        apply_offset_to_bboxes.s(offset=offset)

    return chain()
