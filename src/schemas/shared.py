from typing import Annotated

from geoalchemy2 import WKTElement
from pydantic import BaseModel, Field, NonNegativeFloat, PositiveFloat


class Keypoint(BaseModel):
    """Represents a 2D coordinate point."""
    x: NonNegativeFloat
    y: NonNegativeFloat


class BoundingBox(BaseModel):
    """Represents a 2D bounding box."""
    x: NonNegativeFloat
    y: NonNegativeFloat
    width: PositiveFloat
    height: PositiveFloat

    def convert_to_wkt(self) -> WKTElement:
        x1, y1, x2, y2 = self.x, self.y, self.x + self.width, self.y + self.height

        return WKTElement(
            f"POLYGON(({x1} {y1}, {x2} {y1}, {x2} {y2}, {x1} {y2}, {x1} {y1}))",
            srid=4326
        )


class HTTPError(BaseModel):
    """Represents an HTTP error."""
    detail: str

    class Config:
        json_schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }


CUID = Annotated[
    str,
    Field(
        pattern=r"^c[a-z0-9]{24}$",
        json_schema_extra={
            "format": "cuid",
        },
        description="A unique identifier.",
        example="cltstu4pu0001do2i6vdmtgkz"
    )
]
