"""Add attachments to messages.

Revision ID: c4a8e1d7f234
Revises: f9879bf8236e
"""
from alembic import op
import sqlalchemy as sa

revision = "c4a8e1d7f234"
down_revision = "f9879bf8236e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("messages") as batch_op:
        batch_op.add_column(sa.Column("attachment_path", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("attachment_name", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("attachment_mime", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("attachment_size", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("attachment_type", sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table("messages") as batch_op:
        batch_op.drop_column("attachment_type")
        batch_op.drop_column("attachment_size")
        batch_op.drop_column("attachment_mime")
        batch_op.drop_column("attachment_name")
        batch_op.drop_column("attachment_path")
