import base64
from io import BytesIO

from fastapi import UploadFile
from PIL import Image


async def load_image(image: UploadFile | str) -> Image:
    if isinstance(image, str):
        bytes = base64.b64decode(image)
    else:
        bytes = await image.read()
    return Image.open(BytesIO(bytes))
