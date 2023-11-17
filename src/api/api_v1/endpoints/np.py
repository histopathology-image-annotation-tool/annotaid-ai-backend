import uuid

import numpy as np
from celery.result import AsyncResult
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.celery import celery_app
from src.schemas.celery import AsyncTaskResponse
from src.schemas.np import NPLabel, NPPredictRequest, NPPredictResponse
from src.utils.api import load_image

router = APIRouter()


@router.post(
    '/models/np/predict',
    response_model=AsyncTaskResponse,
    status_code=202
)
async def predict_np(request: NPPredictRequest) -> AsyncTaskResponse:
    """Endpoint for initiating a nuclear pleomorphism classification task."""
    image = await load_image(request.image)
    image = np.array(image)

    task = celery_app.send_task('src.celery.np.tasks.predict_np_task', kwargs={
        'image': image
    })

    return {
        'task_id': task.task_id,
        'status': task.status
    }


@router.get(
    '/models/np/result',
    response_model=NPPredictResponse,
    responses={
        202: {'model': AsyncTaskResponse}
    }
)
async def get_np_result(task_id: uuid.UUID) -> NPPredictResponse:
    """Endpoint for retrieving the result of a nuclear pleomorphism classification task.
    If the provided task_id doesn't belong to any submitted task,
    the PENDING status is returned.
    The task result is deleted immediately after the first read.
    """
    task = AsyncResult(str(task_id))

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
