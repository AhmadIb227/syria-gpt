from alembic import op
import sqlalchemy as sa

revision = '20250101_000002'
down_revision = '20250101_000001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('two_factor_secret', sa.String(length=64), nullable=True))


def downgrade():
    op.drop_column('users', 'two_factor_secret')


