"""Add is_reported field to reviews

Revision ID: add_review_report
Revises: 21bd3b74b271
Create Date: 2025-11-13 15:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_review_report'
down_revision = '21bd3b74b271'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_reported column to reviews table
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_reported', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    # Remove is_reported column from reviews table
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_column('is_reported')

