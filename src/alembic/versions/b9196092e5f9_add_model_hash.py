"""add_model_hash

Revision ID: b9196092e5f9
Revises: b5763623f544
Create Date: 2024-04-13 15:29:02.294749

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b9196092e5f9'
down_revision: str | None = 'b5763623f544'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "predictions",
        sa.Column(
            "model_hash",
            sa.String(10),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column("predictions", "model_hash")
