"""change x y battery to float

Revision ID: a1b2c3d4e5f6
Revises: 05c1e7cc4286
Create Date: 2026-07-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '05c1e7cc4286'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('robots', 'x', existing_type=sa.Integer(), type_=sa.Float())
    op.alter_column('robots', 'y', existing_type=sa.Integer(), type_=sa.Float())
    op.alter_column('robots', 'battery', existing_type=sa.Integer(), type_=sa.Float())


def downgrade() -> None:
    op.alter_column('robots', 'battery', existing_type=sa.Float(), type_=sa.Integer())
    op.alter_column('robots', 'y', existing_type=sa.Float(), type_=sa.Integer())
    op.alter_column('robots', 'x', existing_type=sa.Float(), type_=sa.Integer())
