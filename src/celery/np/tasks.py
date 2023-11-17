import numpy as np

from src.core.celery import celery_app
from src.models import predict_nuclear_pleomorphism

from .definitions import NPPredictTask


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=NPPredictTask
)
def predict_np_task(
    self: NPPredictTask,
    image: np.ndarray
) -> int:
    return predict_nuclear_pleomorphism(
        model=self.model,
        image=image,
        device=self.device
    )
