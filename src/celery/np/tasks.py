import numpy as np

from src.core.celery import celery_app
from src.models import predict_nuclear_pleomorphism

from .definitions import NPPredictTask


@celery_app.task(
    ignore_result=False,
    track_started=True,
    bind=True,
    base=NPPredictTask,
)
def predict_np_task(
    self: NPPredictTask,
    image: np.ndarray
) -> int:
    """Predicts the nuclear pleomorphism score for the input image.

    Args:
        image (np.ndarray): The input image.
    Returns:
        int: The nuclear pleomorphism score (1, 2, or 3).
    """
    return predict_nuclear_pleomorphism(
        model=self.model,
        image=image,
        device=self.device
    )
