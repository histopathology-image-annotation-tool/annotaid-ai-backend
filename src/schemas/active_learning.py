from datetime import datetime
from pathlib import Path
from typing import Generic, TypeVar
from uuid import UUID

from geoalchemy2 import WKTElement
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    field_validator,
    model_validator,
)
from shapely import Polygon, wkb

from .shared import BoundingBox


class WholeSlideImage(BaseModel):
    """Represents a whole slide image."""
    id: UUID
    hash: str = Field(
        default=...,
        description="The SHA256 hash of the slide in base64 format."
    )
    path: Path = Field(
        default=...,
        description="The path to the slide."
    )
    directory: Path
    filename: str
    extension: str
    format: str
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def transform(cls, values):
        path = Path(values['path'])
        values['directory'] = path.parent
        values['filename'] = path.stem
        values['extension'] = path.suffix
        return values
    
    @field_validator('path', 'directory', mode="after")
    @classmethod
    def transform_path(cls, path: Path) -> str:
        return path.as_posix()
    

class Prediction(BaseModel):
    id: UUID
    wsi_id: UUID
    bbox: BoundingBox
    probability: NonNegativeFloat
    label: str
    created_at: datetime
    updated_at: datetime

    @field_validator('bbox', mode="before")
    @classmethod
    def transform(cls, bbox: WKTElement) -> BoundingBox:
        polygon: Polygon = wkb.loads(bytes(bbox.data))
        coords = list(polygon.exterior.coords)

        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]

        x1 = min(x_coords)
        y1 = min(y_coords)
        x2 = max(x_coords)
        y2 = max(y_coords)

        return BoundingBox(
            x=x1,
            y=y1,
            width=x2 - x1,
            height=y2 - y1
        )


class ALPredictSlideRequest(BaseModel):
    """Represents a request containing information about a slide to be predicted."""
    id: UUID


class Annotation(BaseModel):
    """Represents an annotation."""
    id: UUID
    user_id: str
    bbox: BoundingBox
    label: str
    message: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator('bbox', mode="before")
    @classmethod
    def transform(cls, bbox: WKTElement) -> BoundingBox:
        polygon: Polygon = wkb.loads(bytes(bbox.data))
        coords = list(polygon.exterior.coords)

        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]

        x1 = min(x_coords)
        y1 = min(y_coords)
        x2 = max(x_coords)
        y2 = max(y_coords)

        return BoundingBox(
            x=x1,
            y=y1,
            width=x2 - x1,
            height=y2 - y1
        )
    

class Counts(BaseModel):
    """Represents the mitotic counts."""
    mitosis: NonNegativeInt
    hard_negative_mitosis: NonNegativeInt
    

class WholeSlideImageWithCounts(BaseModel):
    """Represents a response containing a list of slides."""
    slide: WholeSlideImage
    counts: Counts


class UpdateSlideAnnotationRequest(BaseModel):
    """Represents a request to update an annotation."""
    user_id: str
    bbox: BoundingBox
    label: str
    message: str | None = None


M = TypeVar('M', bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[M]):
    total: int = Field(description='Number of total items')
    items: list[M] = Field(description='List of items returned in a paginated response')
    page: NonNegativeInt = Field(
        ...,
        description='current page number'
    )
    pages: NonNegativeInt = Field(
        ...,
        description='total number of pages'
    )
    next_page: AnyHttpUrl | None = Field(
        None,
        description='url of the next page if it exists'
    )
    previous_page: AnyHttpUrl | None = Field(
        None,
        description='url of the previous page if it exists'
    )
