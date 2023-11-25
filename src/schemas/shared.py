from pydantic import BaseModel, NonNegativeFloat, PositiveFloat


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
