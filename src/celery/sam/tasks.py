import numpy as np
from PIL import Image
from ultralytics import SAM
from ultralytics.engine.results import Results

from src.core.celery import celery_app
from src.schemas.nuclick import Keypoint

from .definitions import SAMTask


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=SAMTask
)
def predict_sam_task(
    self: SAM,
    image: np.ndarray,
    bboxes: list[np.ndarray]
) -> list[list[Keypoint]]:
    result: Results = self.model(image, bboxes=bboxes)[0].cpu()

    masks = result.masks

    mask = np.zeros_like(masks.orig_shape)

    coords = masks.xy[0]

    for coord in coords:
        x, y = coord[0], coord[1]
        mask[y, x] = 255

    pokus = Image.fromarray(mask)
    pokus.save('./pokus.png')

    return result
