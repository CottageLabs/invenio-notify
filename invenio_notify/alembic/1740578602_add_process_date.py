#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""add process_date"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1740578602'
down_revision = 'cc90a76e9749'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column('notify_inbox', sa.Column('process_date', sa.DateTime(), nullable=True))


def downgrade():
    """Downgrade database."""
    op.drop_column('notify_inbox', 'process_date')
