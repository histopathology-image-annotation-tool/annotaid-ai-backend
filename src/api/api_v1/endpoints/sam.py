import uuid

import numpy as np
from celery.result import AsyncResult
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.celery import celery_app
from src.schemas.celery import AsyncTaskResponse
from src.schemas.sam import SAMPredictRequest, SAMPredictResponse
from src.schemas.shared import BoundingBox
from src.utils.api import load_image

router = APIRouter()


@router.post(
    '/models/sam',
    response_model=AsyncTaskResponse,
)
async def predict_sam(request: SAMPredictRequest) -> AsyncTaskResponse:
    """Endpoint for the SAM segmentation."""
    image = await load_image(request.image)
    image = np.array(image)

    def convert_bbox_to_xyxy(bbox: BoundingBox) -> np.ndarray:
        return np.array([bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height])

    task = celery_app.send_task(
        'src.celery.sam.tasks.predict_sam_task',
        kwargs={
            'image': image,
            'bboxes': [convert_bbox_to_xyxy(bbox) for bbox in request.bboxes]
        }
    )

    return {
        'task_id': task.task_id,
        'status': task.status
    }


@router.get(
    '/models/sam',
    response_model=SAMPredictResponse,
    responses={
        202: {'model': AsyncTaskResponse}
    }
)
async def get_predict_sam_result(
    task_id: uuid.UUID
) -> SAMPredictResponse:
    """Endpoint for retrieving the result of a nuclei segmentation task.
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
    task.forget()

    return {
        'segmented_object': result
    }
