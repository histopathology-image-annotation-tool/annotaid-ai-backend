"""create tables for AL

Revision ID: a86460e5b39e
Revises:
Create Date: 2024-04-05 18:14:17.769023

"""
from collections.abc import Sequence

import sqlalchemy as sa
from geoalchemy2 import Geometry

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a86460e5b39e'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'slides',
        sa.Column(
            'id',
            sa.UUID(as_uuid=True),
            primary_key=True,
            default=sa.text("uuid_generate_v4()")
        ),
        sa.Column(
            'hash',
            sa.String(256),
            nullable=False,
            unique=True,
            index=True
        ),
        sa.Column(
            'path',
            sa.String(256),
            nullable=False
        ),
        sa.Column(
            'format',
            sa.String(20),
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()")
        )
    )

    op.create_table(
        'predictions',
        sa.Column(
            'id',
            sa.UUID(as_uuid=True),
            primary_key=True
        ),
        sa.Column(
            'slide_id',
            sa.UUID(as_uuid=True),
            sa.ForeignKey('slides.id', ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        sa.Column(
            'bbox',
            Geometry(geometry_type="POLYGON", srid=4326),
            nullable=False
        ),
        sa.Column('probability', sa.Float, nullable=False),
        sa.Column('label', sa.String(25), nullable=False),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()")
        )
    )
    sa.Enum('MC_TASK', name='prediction_type').create(op.get_bind())
    op.add_column(
        'predictions',
        sa.Column(
            'type',
            sa.Enum('MC_TASK', name='prediction_type'),
            nullable=False
        )
    )
    op.create_index(
        'idx_order_probability_asc',
        'predictions',
        [sa.asc('probability')],
        unique=False,
        postgresql_using='btree',
    )

    op.create_table(
        'annotations',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(25), nullable=False, index=True),
        sa.Column(
            'prediction_id',
            sa.UUID(as_uuid=True),
            sa.ForeignKey('predictions.id', ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        sa.Column(
            'bbox',
            Geometry(geometry_type="POLYGON", srid=4326)
        ),
        sa.Column(
            'label',
            sa.String(25),
            nullable=False
        ),
        sa.Column('message', sa.String(256)),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()")
        )
    )
    op.create_index(
        'idx_order_created_at_desc',
        'annotations',
        [sa.desc('created_at')],
        unique=False,
        postgresql_using='btree',
    )


def downgrade() -> None:
    op.drop_table('annotations')
    op.drop_table('predictions')
    op.drop_table('slides')
    sa.Enum('MC_TASK', name='prediction_type').drop(op.get_bind())
