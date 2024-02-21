from typing import Any

import torch

from celery import Task
from src.core.config import settings
from src.models import NuClick_NN


class NuclickTask(Task):
    """The task for the NuClick prediction pipeline."""
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
