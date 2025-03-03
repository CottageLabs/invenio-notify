#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""add process_date"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1740578602'
down_revision = 'cc90a76e9749'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column('notify_inbox', sa.Column('process_date', sa.DateTime(), nullable=True))

    # Add the user_id column with foreign key constraint
    op.add_column('notify_inbox', sa.Column('user_id', sa.Integer(), nullable=False))

    # Add foreign key constraint with ON DELETE CASCADE
    op.create_foreign_key(
        'fk_notify_inbox_user',  # Constraint name
        'notify_inbox',  # Table name
        'accounts_user',  # Referenced table
        ['user_id'],  # Column in notify_inbox
        ['id'],  # Column in users
        ondelete='NO ACTION'  # Enables cascade delete
    )

    # Create an index on user_id for performance
    op.create_index('idx_notify_inbox_user_id', 'notify_inbox', ['user_id'])


def downgrade():
    """Downgrade database."""
    op.drop_column('notify_inbox', 'process_date')

    # Drop the foreign key constraint first
    op.drop_constraint('fk_notify_inbox_user', 'notify_inbox', type_='foreignkey')

    # Drop the index
    op.drop_index('idx_notify_inbox_user_id', table_name='notify_inbox')

    # Remove the column
    op.drop_column('notify_inbox', 'user_id')
