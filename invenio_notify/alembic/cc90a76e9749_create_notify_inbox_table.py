"""create notify_inbox table

Revision ID: cc90a76e9749
Revises: 
Create Date: 2025-01-08 13:12:36.133244

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cc90a76e9749'
down_revision = None
branch_labels = ('invenio_notify',)
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notify_inbox",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("raw", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notify_inbox")),
    )


def downgrade() -> None:
    op.drop_table("notify_inbox")
