import uuid

import pytest

from invenio_notify.records.models import NotifyInboxModel
from tests.fixtures.inbox_payload import payload_review
from tests.utils import resolve_user_id


@pytest.fixture
def create_inbox(db, superuser_identity):
    """Fixture to create a NotifyInboxModel instance."""

    def _create_inbox(record_id='r1', raw=None, user_id=None, identity=None, notification_id=None):
        """Create a NotifyInboxModel instance.
        
        Args:
            record_id: Record ID to associate with the inbox
            raw: Raw data content (default: 'test')
            user_id: User ID to associate with the inbox (overrides identity)
            identity: Identity object to get user_id from (defaults to superuser_identity)
            notification_id: Notification ID (defaults to the ID from raw data or auto-generated)
            
        Returns:
            NotifyInboxModel instance
        """
        user_id = resolve_user_id(user_id, identity, superuser_identity)
        if raw is None:
            raw = payload_review('record-not-exists')
        
        # Extract notification_id from raw data if not provided
        if notification_id is None:
            notification_id = raw.get('id', f'urn:uuid:{uuid.uuid4()}')

        inbox = NotifyInboxModel.create({
            'notification_id': notification_id,
            'raw': raw,
            'record_id': record_id,
            'user_id': user_id
        })
        return inbox

    return _create_inbox


