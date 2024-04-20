from pathlib import Path

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt


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
    """Response model for the get slide metadata endpoint from the reader service"""
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
