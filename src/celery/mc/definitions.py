from typing import Any

import torch
import torch.nn as nn
import torchvision
from torchvision.models import EfficientNet
from ultralytics import YOLO

from celery import Task
from src.core.config import settings


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
