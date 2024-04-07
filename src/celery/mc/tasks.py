import numpy as np
from monai.apps.pathology.transforms.stain.array import NormalizeHEStains
from sahi.predict import get_sliced_prediction

from celery import Task
from src.celery.shared.tasks import noop
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
    """Gets the mitotic candidates.

    Args:
        image (np.ndarray): The input image.
    Returns:
        list[np.ndarray]: The bounding boxes of the detected candidates.
    """
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
    """
    Classifies the mitotic candidates.

    Args:
        bboxes (list[np.ndarray]): The bounding boxes of the detected candidates.
        image (np.ndarray): The normalized input image.

    Returns:
        list[MitosisPrediction]: The predictions for the mitotic candidates.
    """
    return predict_mc_second_stage(
        model=self.model,
        image=image,
        bboxes=bboxes,
        device=self.device
    )


@celery_app.task(ignore_result=True)
def apply_offset_to_bboxes(
    mitosis_predictions: list[MitosisPrediction],
    offset: tuple[int, int]
) -> list[MitosisPrediction]:
    """Applies offset to the bounding boxes.

    Args:
        mitosis_predictions (list[MitosisPrediction]): The predictions for the mitotic
        candidates.
        offset (tuple[int, int]): The offset to be applied to the bounding boxes.

    Returns:
        list[MitosisPrediction]: The predictions for the mitotic candidates
        with the offset applied.
    """
    bbox_offset = np.array([*offset, *offset], dtype=np.int32)

    for result in mitosis_predictions:
        result['bbox'] += bbox_offset

    return mitosis_predictions


@celery_app.task(bind=True, ignore_result=True)
def _predict_mc_task(
    self: Task,
    image: np.ndarray,
    offset: tuple[int, int]
) -> list[MitosisPrediction]:
    """Detects the mitotic and hard-negative mitotic cells in the input image.

    Args:
        image (np.ndarray): The input image of at least 512x512 pixels.
        offset (tuple[int, int]): The offset to be applied to the bounding boxes.
    Returns:
        list[MitosisPrediction]: The predictions for the mitotic candidates.
    """
    sig = predict_mc_first_stage_task.s(image=image) | \
        predict_mc_second_stage_task.s(image=image) | \
        apply_offset_to_bboxes.s(offset=offset)

    return self.replace(sig)


@celery_app.task(ignore_result=False, track_started=True)
def predict_mc_task(
    image: np.ndarray,
    offset: tuple[int, int]
) -> list[MitosisPrediction]:
    """Detects the mitotic and hard-negative mitotic cells in the input image.

    Args:
        image (np.ndarray): The input image of at least 512x512 pixels.
        offset (tuple[int, int]): The offset to be applied to the bounding boxes.
    Returns:
        list[MitosisPrediction]: The predictions for the mitotic candidates.
    """
    # When _predict_mc_task is called, it does not return a result, so we use noop
    # (temporary solution until we find a better way to handle this case)
    chain = _predict_mc_task.s(image, offset) | noop.s()
    return chain()
