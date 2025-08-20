"""Add google_id and is_active columns to users table

Revision ID: 0fd0b4b32fdd
Revises: 80cda7fb29a3
Create Date: 2025-08-20 17:38:58.424698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fd0b4b32fdd'
down_revision: Union[str, None] = '80cda7fb29a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add google_id column
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=False)
    
    # Add is_active column
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))


def downgrade() -> None:
    # Remove is_active column
    op.drop_column('users', 'is_active')
    
    # Remove google_id column and its constraints
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_constraint('uq_users_google_id', 'users', type_='unique')
    op.drop_column('users', 'google_id')
