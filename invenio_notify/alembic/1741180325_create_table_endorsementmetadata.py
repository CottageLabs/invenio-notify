#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""create table EndorsementMetadata"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1741180325'
down_revision = None
branch_labels = ('invenio_notify',)
depends_on = None


def upgrade():
    op.create_table(
        "endorsement_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.UUID(), nullable=True),
        sa.Column("reviewer_id", sa.Text(), nullable=False),
        sa.Column("review_type", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("inbox_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_endorsement_metadata")),
        sa.ForeignKeyConstraint(
            ["record_id"],
            ["rdm_record_metadata.id"],
            name=op.f("fk_endorsement_metadata_record_id"),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_endorsement_metadata_user_id"),
            ondelete="NO ACTION"
        ),
        sa.ForeignKeyConstraint(
            ["inbox_id"],
            ["notify_inbox.id"],
            name=op.f("fk_endorsement_metadata_inbox_id"),
            ondelete="NO ACTION"
        ),
        sa.Index(
            "ix_endorsement_metadata_record_id",
            "record_id"
        ),
        sa.Index(
            "ix_endorsement_metadata_user_id",
            "user_id"
        )
    )


def downgrade():
    """Downgrade database."""
    op.drop_table("endorsement_metadata")
