import asyncio

import numpy as np
import redis
from fastapi import APIRouter

from src.schemas.nuclick import NuclickPredictRequest, NuclickPredictResponse
from src.utils.utils import load_image
from src.worker import predict_nuclick_task

router = APIRouter()

r = redis.Redis.from_url('redis://127.0.0.1:6379/0')


@router.post(
    '/models/nuclick/predict',
    response_model=NuclickPredictResponse,
)
async def predict_nuclick(request: NuclickPredictRequest) -> NuclickPredictResponse:
    """Endpoint for the nuclei segmentation."""
    image = await load_image(request.image)
    image = np.array(image)

    task = predict_nuclick_task.delay(
        image=image,
        keypoints=request.keypoints,
        offset=(0, 0) if request.offset is None
        else (request.offset.x, request.offset.y)
    )

    while True:
        if r.exists(f'celery-task-meta-{task.task_id}'):
            break
        await asyncio.sleep(0.3)

    result = task.get()
    task.forget()

    return {
        'segmented_nuclei': result
    }
