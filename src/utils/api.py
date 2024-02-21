import base64
from io import BytesIO

from fastapi import UploadFile
from PIL import Image


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
