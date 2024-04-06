import datetime
import uuid
from typing import Literal, get_args

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import (
    TIMESTAMP,
    UUID,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class WholeSlideImage(Base):
    __tablename__ = "slides"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    predictions: Mapped[list['Prediction']] = relationship(
        "Prediction",
        back_populates="slide",
        lazy="selectin"
    )
    hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        index=True,
        unique=True
    )
    path: Mapped[str] = mapped_column(String(256), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()")
    )


PredictionType = Literal["MC_TASK"]


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    type: Mapped[PredictionType] = mapped_column(
        Enum(
            *get_args(PredictionType),
            name="prediction_type",
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False
    )
    slide: Mapped["WholeSlideImage"] = relationship(
        'WholeSlideImage',
        back_populates="predictions",
        lazy="selectin"
    )
    slide_id: Mapped[UUID] = mapped_column(
        ForeignKey('slides.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    annotations: Mapped[list['Annotation']] = relationship(
        "Annotation",
        back_populates="prediction",
        lazy="selectin"
    )
    bbox: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True),
    )
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    label: Mapped[str] = mapped_column(String(15), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()")
    )

    __table_args__ = (
        Index(
            "order_probability_asc_idx",
            "probability",
            postgresql_using="btree",
            postgresql_ops={"probability": "ASC"}
        ),
    )


class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(25), nullable=False, index=True)
    prediction: Mapped["Prediction"] = relationship(
        'Prediction',
        back_populates="annotations",
        lazy="selectin"
    )
    prediction_id: Mapped[UUID] = mapped_column(
        ForeignKey('predictions.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    bbox: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True),
    )
    label: Mapped[str] = mapped_column(String(15), nullable=False)
    message: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()")
    )

    __table_args__ = (
        Index(
            "order_created_at_desc_idx",
            "created_at",
            postgresql_using="btree",
            postgresql_ops={"created_at": "DESC"}
        ),
    )
