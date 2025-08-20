"""Add first_name and last_name to users table

Revision ID: 80cda7fb29a3
Revises: 
Create Date: 2025-08-20 17:19:07.161245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80cda7fb29a3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add first_name and last_name columns to users table
    op.add_column('users', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(100), nullable=True))


def downgrade() -> None:
    # Remove first_name and last_name columns from users table
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
