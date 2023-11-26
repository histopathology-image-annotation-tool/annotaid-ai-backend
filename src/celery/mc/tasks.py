import numpy as np
from monai.apps.pathology.transforms.stain.array import NormalizeHEStains
from sahi.predict import get_sliced_prediction

from src.core.celery import celery_app
from src.models import predict_mc_second_stage
from src.models.mc.custom_types import MitosisPrediction

from .definitions import MCFirstStageTask, MCSecondStageTask


@celery_app.task(
    ignore_result=True,
    bind=True,
    base=MCFirstStageTask
)
def predict_mc_first_stage_task(
    self: MCFirstStageTask,
    image: np.ndarray
) -> list[np.ndarray]:
    candidates: list[np.ndarray] = []

    try:
        normalizer = NormalizeHEStains()
        normalized_image = normalizer(image)
    except ValueError:
        return candidates

    predicted_objects = get_sliced_prediction(
        image=normalized_image,
        detection_model=self.model,
        slice_width=512,
        slice_height=512,
        overlap_width_ratio=0.25,
        overlap_height_ratio=0.25,
    )

    candidates.extend([
        np.array(object.bbox.to_xyxy(), dtype=np.int32)
        for object in predicted_objects.object_prediction_list
    ])

    return candidates


@celery_app.task(
    ignore_result=True,
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
