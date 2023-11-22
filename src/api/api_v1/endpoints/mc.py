import uuid

import numpy as np
from celery.result import AsyncResult
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.celery import celery_app
from src.schemas.celery import AsyncTaskResponse
from src.schemas.mc import MCPredictRequest, MCPredictResponse, MitosisLabel
from src.utils.api import load_image

router = APIRouter()


@router.post(
    '/models/mc',
    response_model=AsyncTaskResponse,
    status_code=202
)
async def predict_mc(request: MCPredictRequest) -> AsyncTaskResponse:
    """Endpoint for initiating a mitosis detection task."""
    image = await load_image(request.image)
    image = np.array(image)

    offset = [request.offset.x, request.offset.y] \
        if request.offset is not None else [0, 0]

    task = celery_app.send_task('src.celery.mc.tasks.predict_mc_task', kwargs={
        'image': image,
        'offset': offset
    })

    return {'task_id': task.task_id, 'status': task.status}


@router.get(
    '/models/mc',
    response_model=MCPredictResponse,
    responses={
        202: {'model': AsyncTaskResponse}
    }
)
async def get_mc_result(task_id: uuid.UUID) -> MCPredictResponse:
    """Endpoint for retrieving the result of a mitosis detection task.
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

    results = task.get().get()

    for children_task in task.children:
        children_task.forget()
    task.forget()

    def _transform_bbox(bbox: np.ndarray) -> dict[str, float]:
        x1, y1, x2, y2 = bbox

        return {
            'x': x1,
            'y': y1,
            'width': x2 - x1,
            'height': y2 - y1
        }

    return {
        'mitosis': [
            {
                'bbox': _transform_bbox(res['bbox']),
                'confidence': res['conf'],
                'label': MitosisLabel.mitosis if res['label'] == 0
                else MitosisLabel.hard_negative_mitosis
            }
            for res in results
        ]
    }
