import pytest
from invenio_notify.records.models import NotifyInboxModel
from invenio_notify_test.utils import resolve_user_id


@pytest.fixture
def create_inbox(db, superuser_identity):
    """Fixture to create a NotifyInboxModel instance."""
    def _create_inbox(recid='r1', raw='test', user_id=None, identity=None):
        """Create a NotifyInboxModel instance.
        
        Args:
            recid: Record ID to associate with the inbox
            raw: Raw data content (default: 'test')
            user_id: User ID to associate with the inbox (overrides identity)
            identity: Identity object to get user_id from (defaults to superuser_identity)
            
        Returns:
            NotifyInboxModel instance
        """
        user_id = resolve_user_id(user_id, identity, superuser_identity)
            
        inbox = NotifyInboxModel.create({
            'raw': raw, 
            'recid': recid, 
            'user_id': user_id
        })
        return inbox
    return _create_inbox
