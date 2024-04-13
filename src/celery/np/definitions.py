import hashlib
from typing import Any

import torch
from efficientnet_pytorch import EfficientNet

from celery import Task
from src.core.config import settings


class NPPredictTask(Task):
    """The task for the nuclear pleomorphism prediction pipeline."""
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: EfficientNet = None
        self.model_hash: str | None = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            model = EfficientNet.from_name('efficientnet-b0', num_classes=3)
            model.to(self.device)

            checkpoint = torch.load(settings.NP_MODEL_PATH, map_location=self.device)

            model.load_state_dict(checkpoint['model_state_dict'])

            self.model = model

            with open(settings.NP_MODEL_PATH, 'rb') as model_file:
                self.model_hash = hashlib.md5(model_file.read()).hexdigest()

        return self.run(*args, **kwargs)
