import hashlib
from typing import Any

import torch
from efficientnet_pytorch import EfficientNet
from sahi import AutoDetectionModel

from celery import Task
from src.core.config import settings


class MCFirstStageTask(Task):
    """The first stage of the mitotic count prediction pipeline.
    This stage is reposible for detecting candidates in the input image."""
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: AutoDetectionModel = None
        self.model_hash: str | None = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            self.model = AutoDetectionModel.from_pretrained(
                model_type='yolov8',
                model_path=settings.MC_FIRST_STAGE_MODEL_PATH,
                confidence_threshold=0.25,
                device=self.device,
            )

            with open(settings.MC_FIRST_STAGE_MODEL_PATH, 'rb') as model_file:
                self.model_hash = hashlib.md5(model_file.read()).hexdigest()

        return self.run(*args, **kwargs)


class MCSecondStageTask(Task):
    """The second stage of the mitotic count prediction pipeline.
    This stage is responsible for classifying the candidates detected
    in the first stage."""
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: EfficientNet = None
        self.model_hash: str | None = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            checkpoint = torch.load(
                settings.MC_SECOND_STAGE_MODEL_PATH,
                map_location='cpu'
            )

            model = EfficientNet.from_name(
                'efficientnet-b4',
                in_channels=3,
                num_classes=2
            )

            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)

            self.model = model

            with open(settings.MC_SECOND_STAGE_MODEL_PATH, 'rb') as model_file:
                self.model_hash = hashlib.md5(model_file.read()).hexdigest()

        return self.run(*args, **kwargs)
