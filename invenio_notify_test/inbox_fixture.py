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


def create_notification_data(record_id):
    """Create notification data with a real record ID."""

    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "name": "Peer Community in Evolutionary Biology",
            "type": "Service"
        },
        "context": {
            "id": f"https://127.0.0.1:5000/records/{record_id}"
        },
        "id": "urn:uuid:94ecae35-dcfd-4182-8550-22c7164fe23f",
        "inReplyTo": "urn:uuid:0370c0fb-bb78-4a9b-87f5-bed307a509dd",
        "object": {
            "id": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794#review-3136",
            "ietf:cite-as": "",
            "type": [
                "Page",
                "sorg:WebPage"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": [
            "Announce",
            "coar-notify:ReviewAction"
        ]
    }
