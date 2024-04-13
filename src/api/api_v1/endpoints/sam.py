import asyncio
import uuid
from collections import defaultdict
from functools import reduce
from typing import Annotated, Any

import numpy as np
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from redis import Redis

from celery.result import AsyncResult
from src.core.celery import celery_app
from src.core.redis import get_redis_session
from src.schemas.celery import AsyncTaskResponse
from src.schemas.sam import (
    GetSAMEmbeddingsRequest,
    SAMKeypoint,
    SAMPredictRequest,
    SAMPredictResponse,
)
from src.schemas.shared import BoundingBox, HTTPError
from src.utils.api import exist_task, load_image

router = APIRouter()

GET_SAM_EMBEDDINGS_TASK_NAME = 'src.celery.sam.tasks.get_sam_embeddings_task'


@router.post(
    '/models/sam/embeddings',
    response_model=AsyncTaskResponse,
)
async def get_sam_embeddings(request: GetSAMEmbeddingsRequest) -> AsyncTaskResponse:
    """Endpoint for the extraction of SAM encoder embeddings."""
    image = await load_image(request.image)
    image = np.array(image)

    task = celery_app.send_task(
        GET_SAM_EMBEDDINGS_TASK_NAME,
        kwargs={
            'image': image,
        }
    )

    return {
        'task_id': task.task_id,
        'status': task.status
    }


@router.get(
    '/models/sam/embeddings',
    response_model=AsyncTaskResponse,
    responses={
        202: {'model': AsyncTaskResponse},
        404: {'model': HTTPError}
    }
)
async def get_sam_embeddings_result(
    task_id: uuid.UUID,
    db_redis: Redis = Depends(get_redis_session)
) -> AsyncTaskResponse:
    """Endpoint for retrieving the status for the extraction of SAM encoder embeddings.
    If the embeddings are ready to use, the SUCCESS status is returned.
    """
    if not exist_task(db_redis, task_id):
        raise HTTPException(status_code=404, detail='Task not found')

    task = AsyncResult(str(task_id))

    if task.name != GET_SAM_EMBEDDINGS_TASK_NAME:
        raise HTTPException(status_code=404, detail='Task not found')

    if not task.ready():
        return JSONResponse({
            'task_id': str(task_id),
            'status': task.state
        }, status_code=202)

    return {
        'task_id': str(task_id),
        'status': task.state
    }


@router.post(
    '/models/sam',
    response_model=SAMPredictResponse
)
async def predict_sam(
    request: Annotated[
        SAMPredictRequest,
        Body(
            openapi_examples=SAMPredictRequest.model_config
            ['json_schema_extra']['openapi_examples']
        )
    ],
    r: Redis = Depends(get_redis_session)
) -> SAMPredictResponse:
    """Endpoint for the SAM segmentation."""
    def _transform_keypoints(
        acc: defaultdict[str, list[Any]],
        keypoint: SAMKeypoint
    ) -> defaultdict[str, list[Any]]:
        acc['coords'].append([keypoint.keypoint.x, keypoint.keypoint.y])
        acc['labels'].append(1 if keypoint.label == 'foreground' else 0)

        return acc

    def _convert_to_xyxy(bbox: BoundingBox) -> np.ndarray:
        return np.array([bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height])

    point_coords: np.ndarray | None = None
    point_labels: np.ndarray | None = None

    if request.keypoints is not None:
        transformed_keypoints: defaultdict[str, list[Any]] = reduce(
            _transform_keypoints,
            request.keypoints,
            defaultdict(list)
        )

        point_coords = np.array(transformed_keypoints['coords'])
        point_labels = np.array(transformed_keypoints['labels'])

    offset = [request.offset.x, request.offset.y] \
        if request.offset is not None else [0, 0]

    task = celery_app.send_task(
        'src.celery.sam.tasks.predict_sam',
        kwargs={
            'embeddings_task_id': request.embeddings_task_id,
            'previous_predict_task_id': request.previous_predict_task_id,
            'point_coords': point_coords,
            'point_labels': point_labels,
            'bbox': _convert_to_xyxy(request.bbox)
            if request.bbox is not None else None,
            'offset': offset,
            'postprocessing': request.postprocessing
        }
    )

    while True:
        if exist_task(r, task.task_id):
            break
        await asyncio.sleep(0.3)

    result = task.get()

    return {
        'segmented_objects': result['segmented_objects'],
        "previous_predict_task_id": task.task_id
    }
