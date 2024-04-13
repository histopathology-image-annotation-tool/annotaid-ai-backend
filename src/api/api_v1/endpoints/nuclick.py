import asyncio
import uuid

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from redis import Redis

from celery.result import AsyncResult
from src.core.celery import celery_app
from src.core.redis import get_redis_session
from src.schemas.celery import AsyncTaskResponse
from src.schemas.nuclick import (
    Keypoint,
    NuclickBBoxDensePredictRequest,
    NuclickPredictRequest,
    NuclickPredictResponse,
)
from src.schemas.shared import HTTPError
from src.utils.api import exist_task, load_image

router = APIRouter()

PREDICT_NUCLICK_TASK_NAME = 'src.celery.nuclick.tasks.predict_nuclick_task'


@router.post(
    '/models/nuclick',
    response_model=NuclickPredictResponse,
)
async def predict_nuclick(
    request: NuclickPredictRequest,
    r: Redis = Depends(get_redis_session)
) -> NuclickPredictResponse:
    """Endpoint for the nuclei segmentation."""
    image = await load_image(request.image)
    image = np.array(image)

    task = celery_app.send_task(
        PREDICT_NUCLICK_TASK_NAME,
        kwargs={
            'image': image,
            'keypoints': request.keypoints,
            'offset': (0, 0) if request.offset is None
            else (request.offset.x, request.offset.y)
        }
    )

    while True:
        if exist_task(r, task.task_id):
            break
        await asyncio.sleep(0.3)

    result = task.get()
    task.forget()

    return {
        'segmented_nuclei': result
    }


@router.post(
    '/models/nuclick/bbox-dense',
    response_model=AsyncTaskResponse
)
async def predict_bbox_dense_annotation(
    request: NuclickBBoxDensePredictRequest
) -> AsyncTaskResponse:
    """Endpoint for the nuclei segmentation defined by bounding boxes.
    The endpoint uses NuClick for the dense prediction and it simulates the user click
    by using the center of the bounding box.
    """
    image = await load_image(request.image)
    image = np.array(image)

    keypoints = [
        Keypoint(
            x=bbox.x + bbox.width / 2,
            y=bbox.y + bbox.height / 2
        )
        for bbox in request.bboxes
    ]

    task = celery_app.send_task(
        PREDICT_NUCLICK_TASK_NAME,
        kwargs={
            'image': image,
            'keypoints': keypoints,
            'offset': (0, 0) if request.offset is None
            else (request.offset.x, request.offset.y)
        }
    )

    return {
        'task_id': task.task_id,
        'status': task.status
    }


@router.get(
    '/models/nuclick/bbox-dense',
    response_model=NuclickPredictResponse,
    responses={
        202: {'model': AsyncTaskResponse},
        404: {'model': HTTPError}
    }
)
async def get_predict_bbox_dense_annotation_result(
    task_id: uuid.UUID,
    db_redis: Redis = Depends(get_redis_session)
) -> NuclickPredictResponse:
    """Endpoint for retrieving the result of a nuclei segmentation task.
    The task result is deleted immediately after the first read.
    """
    if not exist_task(db_redis, task_id):
        raise HTTPException(status_code=404, detail='Task not found')

    task = AsyncResult(str(task_id))

    if task.name != PREDICT_NUCLICK_TASK_NAME:
        raise HTTPException(status_code=404, detail='Task not found')

    if not task.ready():
        return JSONResponse({
            'task_id': str(task_id),
            'status': task.state
        }, status_code=202)

    result = task.get()
    task.forget()

    return {
        'segmented_nuclei': result
    }
