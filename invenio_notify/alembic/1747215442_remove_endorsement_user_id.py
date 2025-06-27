#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""remove endorsement user_id column"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1747215442'
down_revision = '1747215441'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database."""
    # Remove the user_id column and its index/constraints from endorsement table
    op.drop_index('ix_endorsement_user_id', table_name='endorsement')
    op.drop_constraint('fk_endorsement_user_id_accounts_user', 'endorsement', type_='foreignkey')
    op.drop_column('endorsement', 'user_id')


def downgrade():
    """Downgrade database."""
    # Add back the user_id column and its constraints
    op.add_column('endorsement', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_endorsement_user_id_accounts_user', 'endorsement', 'accounts_user', ['user_id'], ['id'], ondelete='NO ACTION')
    op.create_index('ix_endorsement_user_id', 'endorsement', ['user_id'], unique=False)