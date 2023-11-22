from typing import Any

import torch
from ultralytics import SAM

from celery import Task


class SAMTask(Task):
    abstract = True

    def __init__(self) -> None:
        super().__init__()

        self.model: SAM = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.model:
            model = SAM('./models/sam_b.pt')

            model.to(self.device)

            self.model = model

        return self.run(*args, **kwargs)
