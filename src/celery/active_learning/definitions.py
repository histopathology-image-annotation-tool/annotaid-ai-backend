from pathlib import Path

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt

from celery import Task


class PollingException(Exception):
    pass


class PollingTask(Task):
    autoretry_for = (PollingException,)
    retry_kwargs = {'max_retries': 100, 'countdown': 5}
    retry_backoff = True


class PixelsPerMeter(BaseModel):
    avg: NonNegativeFloat
    x: NonNegativeFloat
    y: NonNegativeFloat


class MetadataDimSize(BaseModel):
    micro: NonNegativeFloat
    pixel: NonNegativeFloat


class Size(BaseModel):
    c: NonNegativeInt
    t: NonNegativeInt
    z: NonNegativeInt
    width: MetadataDimSize
    height: MetadataDimSize


class FileSize(BaseModel):
    uncompressed: NonNegativeInt
    compressed: NonNegativeInt


class GetSlideMetadataResponse(BaseModel):
    magnification: NonNegativeInt
    format: str
    domains: list[str]
    resolution: NonNegativeInt
    fillColor: NonNegativeInt
    path: Path
    pixelsPerMeter: PixelsPerMeter
    size: Size
    fileSize: FileSize
    hash: str
    levels: NonNegativeInt
