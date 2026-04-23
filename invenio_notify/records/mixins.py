"""Custom mixins for database models with UTC timestamp support."""

#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

import sqlalchemy as sa
from datetime import datetime, timezone


class UTCTimestamp:
    """Mixin for adding UTC timestamp columns that store UTC datetimes."""

    created = sa.Column(
        sa.DateTime(),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now()
    )
    """Timestamp when the record was created (stored as UTC)."""

    updated = sa.Column(
        sa.DateTime(),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now()
    )
    """Timestamp when the record was last updated (stored as UTC)."""