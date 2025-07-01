import pytest
import uuid

from invenio_notify.records.models import NotifyInboxModel
from invenio_notify_test.utils import resolve_user_id


@pytest.fixture
def create_inbox(db, superuser_identity):
    """Fixture to create a NotifyInboxModel instance."""

    def _create_inbox(recid='r1', raw=None, user_id=None, identity=None, noti_id=None):
        """Create a NotifyInboxModel instance.
        
        Args:
            recid: Record ID to associate with the inbox
            raw: Raw data content (default: 'test')
            user_id: User ID to associate with the inbox (overrides identity)
            identity: Identity object to get user_id from (defaults to superuser_identity)
            noti_id: Notification ID (defaults to the ID from raw data or auto-generated)
            
        Returns:
            NotifyInboxModel instance
        """
        user_id = resolve_user_id(user_id, identity, superuser_identity)
        if raw is None:
            raw = create_inbox_payload__review('record-not-exists')
        
        # Extract noti_id from raw data if not provided
        if noti_id is None:
            noti_id = raw.get('id', f'urn:uuid:{uuid.uuid4()}')

        inbox = NotifyInboxModel.create({
            'noti_id': noti_id,
            'raw': raw,
            'recid': recid,
            'user_id': user_id
        })
        return inbox

    return _create_inbox


def create_inbox_payload__review(record_id, in_reply_to=None) -> dict:
    """Create notification data with a real record ID."""
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()

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
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "id": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794#review-3136",
            "ietf:cite-as": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794#review-3136",
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


def create_inbox_payload__endorsement_request(record_id, in_reply_to=None) -> dict:
    # KTODO how to define value of object.ietf:item.id?
    # KTODO remember to update value of origin.id, origin.inbox when generating request
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "mailto:josiah.carberry@example.com",
            "name": "Josiah Carberry",
            "type": "Person"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "id":  f"https://127.0.0.1:5000/records/{record_id}",
            "ietf:cite-as": "https://doi.org/10.5555/12345680",
            "ietf:item": {
                "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                "mediaType": "application/pdf",
                "type": [
                    "Article",
                    "sorg:ScholarlyArticle"
                ]
            },
            "type": [
                "Page",
                "sorg:AboutPage"
            ]
        },
        "origin": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "target": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "type": [
            "Offer",
            "coar-notify:EndorsementAction"
        ]
    }


def create_inbox_payload__endorsement_resp(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
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
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "id": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794",
            "ietf:cite-as": "https://doi.org/10.24072/pci.evolbiol.100794",
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
            "coar-notify:EndorsementAction"
        ]
    }


def create_inbox_payload__tentative_accept(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
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
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "actor": {
                "id": "https://orcid.org/0000-0002-1825-0097",
                "name": "Josiah Carberry",
                "type": "Person"
            },
            "id": f"urn:uuid:{uuid.uuid4()}",
            "object": {
                "id": f"https://127.0.1:5000/records/{record_id}",
                "ietf:cite-as": "https://doi.org/10.5555/12345680",
                "ietf:item": {
                    "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                    "mediaType": "application/pdf",
                    "type": [
                        "Page",
                        "sorg:AboutPage"
                    ]
                },
                "type": "sorg:AboutPage"
            },
            "origin": {
                "id": "https://research-organisation.org/repository",
                "inbox": "https://research-organisation.org/inbox/",
                "type": "Service"
            },
            "target": {
                "id": "https://overlay-journal.com/system",
                "inbox": "https://overlay-journal.com/inbox/",
                "type": "Service"
            },
            "type": [
                "Offer",
                "coar-notify:EndorsementAction"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "summary": "The offer has been tentatively accepted, subject to further review.",
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": "TentativeAccept"
    }


def create_inbox_payload__reject(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
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
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "actor": {
                "id": "https://orcid.org/0000-0002-1825-0097",
                "name": "Josiah Carberry",
                "type": "Person"
            },
            "id": f"urn:uuid:{uuid.uuid4()}",
            "object": {
                "id": f"https://127.0.1:5000/records/{record_id}",
                "ietf:cite-as": "https://doi.org/10.5555/12345680",
                "ietf:item": {
                    "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                    "mediaType": "application/pdf",
                    "type": [
                        "Page",
                        "sorg:AboutPage"
                    ]
                },
                "type": "sorg:AboutPage"
            },
            "origin": {
                "id": "https://research-organisation.org/repository",
                "inbox": "https://research-organisation.org/inbox/",
                "type": "Service"
            },
            "target": {
                "id": "https://overlay-journal.com/system",
                "inbox": "https://overlay-journal.com/inbox/",
                "type": "Service"
            },
            "type": [
                "Offer",
                "coar-notify:EndorsementAction"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "summary": "The offer has been rejected because...",
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": "Reject"
    }


def create_inbox_payload__tentative_reject(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
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
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "actor": {
                "id": "https://orcid.org/0000-0002-1825-0097",
                "name": "Josiah Carberry",
                "type": "Person"
            },
            "id": f"urn:uuid:{uuid.uuid4()}",
            "object": {
                "id": f"https://127.0.1:5000/records/{record_id}",
                "ietf:cite-as": "https://doi.org/10.5555/12345680",
                "ietf:item": {
                    "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                    "mediaType": "application/pdf",
                    "type": [
                        "Page",
                        "sorg:AboutPage"
                    ]
                },
                "type": "sorg:AboutPage"
            },
            "origin": {
                "id": "https://research-organisation.org/repository",
                "inbox": "https://research-organisation.org/inbox/",
                "type": "Service"
            },
            "target": {
                "id": "https://overlay-journal.com/system",
                "inbox": "https://overlay-journal.com/inbox/",
                "type": "Service"
            },
            "type": [
                "Offer",
                "coar-notify:EndorsementAction"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "summary": "The offer has been tentatively rejected, subject to further review.",
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": "TentativeReject"
    }
