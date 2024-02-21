import uuid

import numpy as np
import torch
from celery.result import AsyncResult, allow_join_result
from imantics import Mask
from segment_anything import SamPredictor
from skimage.morphology import (
    reconstruction,
    remove_small_holes,
    remove_small_objects,
)

from src.core.celery import celery_app
from src.schemas.sam import SAMPredictRequestPostprocessing

from .definitions import SamPredictorConfig, SamPredictTaskResult, SAMTask


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=SAMTask
)
def get_sam_embeddings_task(
    self: SAMTask,
    image: np.ndarray,
) -> SamPredictorConfig:
    """Gets the SAM encoder embeddings for the input image.

    Args:
        image (np.ndarray): The input image.

    Returns:
        SamPredictorConfig: The configuration for the SAM predictor.
    """
    predictor = SamPredictor(self.model)

    predictor.set_image(image)

    features = predictor.get_image_embedding().cpu().numpy()

    predictor_config: SamPredictorConfig = {
        'original_size': predictor.original_size,
        'input_size': predictor.input_size,
        'features': features,
        'is_image_set': predictor.is_image_set
    }

    return predictor_config


@celery_app.task(
    ignore_result=False,
    bind=True,
    base=SAMTask
)
def predict_sam(
    self: SAMTask,
    embeddings_task_id: uuid.UUID,
    previous_predict_task_id: uuid.UUID | None,
    point_coords: np.ndarray | None,
    point_labels: np.ndarray | None,
    bbox: np.ndarray | None,
    offset: tuple[int, int],
    postprocessing: SAMPredictRequestPostprocessing | None
) -> SamPredictTaskResult:
    """Predicts the segmented objects using the SAM model.

    Args:
        embeddings_task_id (uuid.UUID): The task ID with the stored embeddings.
        previous_predict_task_id (uuid.UUID | None): The task ID for the previous
        predict task. If provided, the low resolution segmentation mask of the previous
        prediction is fed to the model to help refine the segmentation result.
        point_coords (np.ndarray | None): The input coordinates of the user clicks.
        point_labels (np.ndarray | None): The labels of the user clicks
        (foreground / background).
        bbox (np.ndarray | None): The bounding box from which the model
        tries to segment objects.
        offset (tuple[int, int]): The offset to be added to the segmented objects.
        postprocessing (SAMPredictRequestPostprocessing | None): The postprocessing
        configuration.
    Returns:
        SamPredictTaskResult: The result of the SAM prediction task.
    """
    embeddings_task = AsyncResult(str(embeddings_task_id))
    previous_predict_task = AsyncResult(str(previous_predict_task_id))

    previous_mask_input: np.ndarray | None = None

    if not embeddings_task.ready():
        raise ValueError(f'Embeddings are not ready: {embeddings_task_id}')

    if previous_predict_task_id is not None and not previous_predict_task.ready():
        raise ValueError('Previous predict task has not finished: '
                         f'{previous_predict_task_id}')

    with allow_join_result():
        predictor_config: SamPredictorConfig = embeddings_task.get()

        if previous_predict_task_id is not None:
            previous_predict_result: SamPredictTaskResult = previous_predict_task.get()
            previous_mask_input = previous_predict_result['low_res_mask']
            previous_mask_input = previous_mask_input[np.newaxis, ...]  # type: ignore

    predictor = SamPredictor(self.model)
    predictor.original_size = predictor_config['original_size']
    predictor.input_size = predictor_config['input_size']
    predictor.features = torch.from_numpy(predictor_config['features']).to(self.device)
    predictor.is_image_set = predictor_config['is_image_set']

    multimask_output = True

    if point_coords is not None:
        multimask_output = False if len(point_coords) > 1 else True

    if bbox is not None:
        multimask_output = False

    if postprocessing is not None and postprocessing.multimask_output is not None:
        multimask_output = postprocessing.multimask_output

    masks, scores, logits = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        mask_input=previous_mask_input,
        box=bbox,
        multimask_output=multimask_output
    )

    highest_score_index = np.argmax(scores)
    best_mask: np.ndarray = masks[highest_score_index]
    low_res_mask: np.ndarray = logits[highest_score_index]

    if postprocessing is not None:
        if postprocessing.min_object_size is not None:
            best_mask = remove_small_objects(
                best_mask,
                min_size=postprocessing.min_object_size
            )
        if postprocessing.remove_holes_smaller_than is not None:
            best_mask = remove_small_holes(
                best_mask,
                area_threshold=postprocessing.remove_holes_smaller_than
            )

        if postprocessing.reconstruction is not None:
            marker_mask = np.zeros_like(best_mask)

            if point_coords is not None:
                for point in point_coords:
                    x, y = point
                    x = int(x)
                    y = int(y)

                    marker_mask[y, x] = best_mask[y, x]

            best_mask = reconstruction(marker_mask, best_mask)

    best_mask = np.where(best_mask > 0.5, 255, 0)

    polygons = Mask(best_mask).polygons()

    return {
        "segmented_objects": [
            [
                {
                    "x": point[0].item() + offset[0],
                    "y": point[1].item() + offset[1]
                }
                for point in points
            ]
            for points in polygons.points
        ],
        "low_res_mask": low_res_mask
    }
