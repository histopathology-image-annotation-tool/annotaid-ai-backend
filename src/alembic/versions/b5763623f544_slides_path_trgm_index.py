"""slides_path_trgm_index

Revision ID: b5763623f544
Revises: a86460e5b39e
Create Date: 2024-04-10 10:41:51.616336

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b5763623f544'
down_revision: str | None = 'a86460e5b39e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_index(
        'idx_path_trgm',
        'slides',
        [sa.text('path gin_trgm_ops')],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index('idx_path_trgm', table_name='slides')
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
