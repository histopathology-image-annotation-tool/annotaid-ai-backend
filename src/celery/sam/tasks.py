import uuid

import numpy as np
import torch
from celery.result import AsyncResult, allow_join_result
from imantics import Mask
from segment_anything import SamPredictor

from src.core.celery import celery_app

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
    point_coords: np.ndarray,
    point_labels: np.ndarray,
    bbox: np.ndarray,
    offset: tuple[int, int]
) -> SamPredictTaskResult:
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

    masks, scores, logits = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        mask_input=previous_mask_input,
        box=bbox,
        multimask_output=True
    )

    highest_score_index = np.argmax(scores)
    best_mask = masks[highest_score_index]
    low_res_mask = logits[highest_score_index]

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
