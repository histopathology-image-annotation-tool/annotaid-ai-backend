import uuid

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from redis import Redis

from celery.result import AsyncResult
from src.core.celery import celery_app
from src.core.redis import get_redis_session
from src.schemas.celery import AsyncTaskResponse
from src.schemas.np import NPLabel, NPPredictRequest, NPPredictResponse
from src.schemas.shared import HTTPError
from src.utils.api import exist_task, load_image

router = APIRouter()

PREDICT_NP_TASK_NAME = 'src.celery.np.tasks.predict_np_task'


@router.post(
    '/models/np',
    response_model=AsyncTaskResponse,
    status_code=202
)
async def predict_np(request: NPPredictRequest) -> AsyncTaskResponse:
    """Endpoint for initiating a nuclear pleomorphism classification task."""
    image = await load_image(request.image)
    image = np.array(image)

    task = celery_app.send_task(PREDICT_NP_TASK_NAME, kwargs={
        'image': image
    })

    return {
        'task_id': task.task_id,
        'status': task.status
    }


@router.get(
    '/models/np',
    response_model=NPPredictResponse,
    responses={
        202: {'model': AsyncTaskResponse},
        404: {'model': HTTPError}
    }
)
async def get_np_result(
    task_id: uuid.UUID,
    db_redis: Redis = Depends(get_redis_session)
) -> NPPredictResponse:
    """Endpoint for retrieving the result of a nuclear pleomorphism classification task.
    The task result is deleted immediately after the first read.
    """
    if not exist_task(db_redis, task_id):
        raise HTTPException(status_code=404, detail='Task not found')

    task = AsyncResult(str(task_id))

    if task.name != PREDICT_NP_TASK_NAME:
        raise HTTPException(status_code=404, detail='Task not found')

    if not task.ready():
        return JSONResponse({
            'task_id': str(task_id),
            'status': task.state
        }, status_code=202)

    result = task.get()

    for children_task in task.children:
        children_task.forget()
    task.forget()

    def _map_label_to_class(label: int) -> NPLabel:
        labels = {
            None: NPLabel.undetermined,
            0: NPLabel.score_1,
            1: NPLabel.score_2,
            2: NPLabel.score_3
        }

        return labels[label]

    return {
        'label': _map_label_to_class(result)
    }
