import uuid

from invenio_base import invenio_url_for
from invenio_records_resources.services.records.results import RecordItem

from invenio_notify.constants import WORKFLOW_STATUS_TENTATIVE_REJECT
from invenio_notify.records.models import ActorModel, EndorsementRequestModel


def _get_user_name(user):
    if 'full_name' in user.user_profile and user.user_profile['full_name']:
        return user.user_profile['full_name']
    elif user.username:
        return user.username

    return user.email

def create_endorsement_request_data(user, record: RecordItem, actor: ActorModel, origin_id=None):
    """Create endorsement request data following COAR notification structure.
    
    Args:
        user: User object making the endorsement request
        record: RecordItem object representing the record
        actor: Actor object containing inbox URL and other details
        origin_id: Origin ID from configuration (optional, will be retrieved from config if not provided)
    """

    if origin_id is None:
        from flask import current_app
        origin_id = current_app.config.get("NOTIFY_ORIGIN_ID", None)
        if not origin_id:
            raise ValueError("NOTIFY_ORIGIN_ID must be set in invenio.cfg")

    # Check for existing TentativeReject reply to include as inReplyTo
    status, noti_id = EndorsementRequestModel.get_latest_status(
        record._record.model.id, actor.id, True
    )

    # define the object structure
    noti_obj = {
        "id": record.data["links"]["self_html"],
        "type": ["Page", "sorg:AboutPage"],
        "ietf:item": {
            "id": record.data["links"]["self_html"],
            "mediaType": "text/html",
            "type": ["Page", "sorg:AboutPage"],
        },
        "ietf:cite-as": record.data["links"]["self_html"],
    }

    if 'doi' in record.data['links']:
        noti_obj['ietf:cite-as'] = record.data['links']['doi']

    # define full notification data structure
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": f"mailto:{user.email}",
            "name": _get_user_name(user),
            "type": "Person"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "object": noti_obj,
        "origin": {
            "id": origin_id,
            "inbox": invenio_url_for('inbox_api.receive_notification'),
            "type": "Service"
        },
        "target": {
            "id": actor.actor_id,
            "inbox": str(actor.inbox_url), # actor.inbox_url is a furl object
            "type": "Service"
        },
        "type": [
            "Offer",
            "coar-notify:EndorsementAction"
        ]
    }
    
    # Add inReplyTo if the last EndorsementRequest has TentativeReject status
    if status == WORKFLOW_STATUS_TENTATIVE_REJECT:
        data["inReplyTo"] = noti_id

    return data
