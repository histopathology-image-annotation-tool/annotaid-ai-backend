import numpy as np

from src.core.celery import celery_app
from src.models import predict_mc_first_stage, predict_mc_second_stage
from src.models.mc.custom_types import MitosisPrediction

from .definitions import MCFirstStageTask, MCSecondStageTask


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
