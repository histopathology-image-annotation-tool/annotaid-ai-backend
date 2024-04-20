from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Generic, Literal, TypeVar, Union
from uuid import UUID

from geoalchemy2 import WKTElement
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    StringConstraints,
    field_validator,
    model_validator,
)
from shapely import Polygon, wkb

from .mc import MitosisLabel
from .shared import CUID, BoundingBox

AnnotationLabel = Annotated[
    Union[MitosisLabel, Literal["unknown"]],
    StringConstraints(max_length=25),
    None,
]


def transform_label(label: str) -> MitosisLabel | str:
    """Transforms the prediction label to a MitosisLabel enum or returns the label as
    is, if it does not match any of the enum values.

    Args:
        label (str): The prediction label (0, 1).

    Returns:
        MitosisLabel | str: The transformed label.
    """
    _mapping: dict[str, MitosisLabel] = {
        "0": MitosisLabel.mitosis,
        "1": MitosisLabel.hard_negative_mitosis
    }

    return _mapping.get(label, label)


def transform_wkt_bbox(bbox: WKTElement) -> BoundingBox:
    """Transforms the wkt bbox to a BoundingBox instance.

    Args:
        bbox (WKTElement): The wkt bbox.

    Returns:
        BoundingBox: The BoundingBox instance.
    """
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
    """Represents counts of annotations for each label."""
    unknown: NonNegativeInt
    mitosis: NonNegativeInt
    hard_negative_mitosis: NonNegativeInt

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> 'Counts':
        """Creates a Counts instance from a dictionary of counts for each label.

        Args:
            data (dict[str, int]): A dictionary of counts for each label.

        Example:
            >>> data = {
            ...     'unknown': 0,
            ...     'mitosis': 1,
            ...     'hard_negative_mitosis': 2
            ... }
            >>> counts = Counts.from_dict(data)
            >>> counts
            Counts(unknown=0, mitosis=1, hard_negative_mitosis=2)

        Returns:
            Counts: The counts instance.
        """
        def _get_data(key: str) -> int:
            _mappings = {
                'mitosis': ['0', 'mitosis'],
                'hard_negative_mitosis': ['1', 'hard_negative_mitosis'],
                'unknown': ['unknown']
            }

            for value in _mappings[key]:
                if value in data:
                    return data[value]

            return 0

        return cls(
            unknown=_get_data('unknown'),
            mitosis=_get_data('mitosis'),
            hard_negative_mitosis=_get_data('hard_negative_mitosis')
        )


class AnnotationMetadata(BaseModel):
    """Represents metadata about annotations for a slide."""
    user_annotated: Counts | None = Field(
        None,
        description="Counts of annotations annotated by the user. "
        "If user_id is not provided, this field is None."
    )
    total: Counts = Field(
        ...,
        description="Counts of annotations predicted by the model"
    )


class WholeSlideImage(BaseModel):
    """Represents a whole slide image."""
    id: UUID
    hash: str = Field(
        default=...,
        description="The SHA256 hash of the slide in base64 format.",
        max_length=256
    )
    path: Path = Field(
        default=...,
        description="The path to the slide.",
        max_length=256
    )
    directory: Path
    filename: str
    extension: str
    format: str = Field(
        ...,
        max_length=20
    )
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def transform(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Extracts the directory, filename, and extension.

        Args:
            values (dict[str, Any]): The values to transform.

        Returns:
            dict[str, Any]: The transformed values.
        """
        path = Path(values['path'])

        values['directory'] = path.parent
        values['filename'] = path.stem
        values['extension'] = path.suffix

        return values

    @field_validator('path', 'directory', mode="after")
    @classmethod
    def transform_path(cls, path: Path) -> str:
        """Transforms the path to a posix string.

        Args:
            path (Path): The path to transform.

        Returns:
            str: The posix string representation of the path.
        """
        return path.as_posix()


class Prediction(BaseModel):
    """Represents an annotation (prediction) by the model."""
    id: UUID
    slide_id: UUID
    bbox: BoundingBox
    probability: NonNegativeFloat = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence of a predicted label"
    )
    label: AnnotationLabel
    created_at: datetime
    updated_at: datetime

    _transform_bbox = field_validator('bbox', mode="before")(transform_wkt_bbox)
    _transform_label = field_validator('label', mode="before")(transform_label)

    @field_validator('probability', mode="after")
    @classmethod
    def transform_probability(cls, probability: float) -> float:
        """Rounds the probability to 4 decimal places.

        Args:
            probability (float): The probability to round.

        Returns:
            float: The rounded probability value.
        """
        return round(probability, 4)


class PredictionWithMetadata(BaseModel):
    """Represents a prediction with metadata."""
    prediction: Prediction
    metadata: AnnotationMetadata


class ALPredictSlideRequest(BaseModel):
    """Represents a request containing information about a slide to be predicted."""
    id: UUID


class Annotation(BaseModel):
    """Represents an annotation."""
    id: UUID
    prediction_id: UUID
    user_id: CUID
    bbox: BoundingBox
    label: AnnotationLabel
    message: str | None = Field(
        None,
        description="Additional message from the user.",
        max_length=256
    )
    created_at: datetime
    updated_at: datetime

    _transform_bbox = field_validator('bbox', mode="before")(transform_wkt_bbox)
    _transform_label = field_validator('label', mode="before")(transform_label)


class WholeSlideImageWithMetadata(BaseModel):
    """Represents a response containing a list of slides."""
    slide: WholeSlideImage
    metadata: AnnotationMetadata


class UpsertSlideAnnotationRequest(BaseModel):
    """Represents a request to upsert an annotation."""
    user_id: CUID
    bbox: BoundingBox
    label: AnnotationLabel
    message: str | None = Field(
        None,
        description="Additional message from the user.",
        max_length=256
    )


class UpsertSlideAnnotationResponse(BaseModel):
    """Represents a response to an upsert annotation request with the next
    prediction to annotate."""
    annotation: Annotation
    next_annotation: Prediction | None = Field(
        None,
        description="The next prediction to annotate."
    )
    metadata: AnnotationMetadata


M = TypeVar('M', bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[M]):
    """Represents a generic paginated response."""
    total: int = Field(description='Number of total items')
    items: list[M] = Field(description='List of items returned in a paginated response')
    page: NonNegativeInt = Field(
        ...,
        description='Current page number'
    )
    pages: NonNegativeInt = Field(
        ...,
        description='Total number of pages'
    )
    next_page: AnyHttpUrl | None = Field(
        None,
        description='Url of the next page if it exists'
    )
    previous_page: AnyHttpUrl | None = Field(
        None,
        description='Url of the previous page if it exists'
    )
