from alembic import op
import sqlalchemy as sa

revision = '20250101_000003'
down_revision = '20250101_000002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'token')


