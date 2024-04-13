import base64
import uuid
from io import BytesIO

from fastapi import UploadFile
from PIL import Image
from redis import Redis


async def load_image(image: UploadFile | str) -> Image:
    """Loads an image from a file or a base64 string.

    Args:
        image (UploadFile | str): The input image.
    Returns:
        Image: The uploaded image.
    """
    if isinstance(image, str):
        bytes = base64.b64decode(image)
    else:
        bytes = await image.read()
    return Image.open(BytesIO(bytes))


def exist_task(redis: Redis, task_id: uuid.UUID) -> bool:
    """Checks if a task exists in the Redis database.

    Args:
        redis (Redis): The Redis database.
        task_id (uuid.UUID): The task ID.
    Returns:
        bool: True if the task exists, False otherwise.
    """
    return redis.exists(f"celery-task-meta-{str(task_id)}")
