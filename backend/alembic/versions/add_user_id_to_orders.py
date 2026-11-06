"""Add user_id to orders for ownership checks

Revision ID: a1b2c3d4e5f6
Revises: f22338f7c904
Create Date: 2026-11-06 07:00:00.000000+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f22338f7c904"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("order", sa.Column("user_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("order", "user_id")