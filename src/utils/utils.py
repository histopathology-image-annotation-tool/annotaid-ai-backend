import base64
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from PIL import Image


async def load_image(image: UploadFile | str) -> Image:
    if isinstance(image, str):
        bytes = base64.b64decode(image)
    else:
        bytes = await image.read()
    return Image.open(BytesIO(bytes))


def read_file(path: Path) -> str:
    with open(path) as fp:
        return fp.read()
