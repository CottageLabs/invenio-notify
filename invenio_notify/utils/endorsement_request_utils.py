import uuid

from invenio_base import invenio_url_for
from invenio_records_resources.services.records.results import RecordItem

from invenio_notify import constants
from invenio_notify.records.models import ActorModel, EndorsementRequestModel, EndorsementModel


def create_endorsement_request_data(user, record: RecordItem, actor: ActorModel, origin_id=None):
    """Create endorsement request data following COAR notification structure.
    
    Args:
        user: User object making the endorsement request
        actor: Actor object containing inbox URL and other details
        origin_id: Origin ID from configuration (optional, will be retrieved from config if not provided)
    """

    if origin_id is None:
        from flask import current_app
        origin_id = current_app.config.get("NOTIFY_ORIGIN_ID", None)
        if not origin_id:
            raise ValueError("NOTIFY_ORIGIN_ID must be set in invenio.cfg")

    # define the object structure
    noti_obj = {
        "id": record.data["links"]["self_html"],
        "type": ["Page", "sorg:AboutPage"],
        "ietf:item": {
            "id": record.data["links"]["self_html"],
            "mediaType": "text/html",
            "type": ["Page", "sorg:AboutPage"],
        },
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
            "name": user.username if user.username else user.email,
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

    return data


def get_overall_endorsement_status(record_id, actor_id):
    # First check if there's an actual endorsement
    status = get_latest_endorsement_status(record_id, actor_id)
    if status:
        return status

    # If no endorsement, check endorsement request status
    status = get_latest_endorsement_request_status(record_id, actor_id)
    if status:
        return status

    return None


def get_available_actors(record_id):
    """Get list of available actors with their endorsement request status.
    
    Args:
        record_id: UUID of the record
        user_id: ID of the user making the request
        
    Returns:
        list: List of actor dictionaries with id, name, and status
    """

    all_actors = ActorModel.query.all()
    actors = []

    for actor in all_actors:
        endo_staus = get_overall_endorsement_status(record_id, actor.id)

        # Set status based on endorsement request
        available = can_send(endo_staus, actor)

        actors.append({
            "actor_id": actor.id,
            "actor_name": actor.name,
            "status": endo_staus or 'available',
            'available': available,
        })

    return actors


def get_latest_endorsement_request_status(record_id, actor_id):
    status = (
        EndorsementRequestModel.query.filter_by(
            record_id=record_id,
            actor_id=actor_id,
        )
        .order_by(EndorsementRequestModel.created.desc())
        .with_entities(EndorsementRequestModel.latest_status)
        .limit(1)
        .scalar())
    return status


def get_latest_endorsement_status(record_id, actor_id):
    status = (
        EndorsementModel.query.filter_by(
            record_id=record_id,
            actor_id=actor_id,
        )
        .order_by(EndorsementModel.created.desc())
        .with_entities(EndorsementModel.review_type)
        .limit(1)
        .scalar())
    return status


def can_send(endo_status, actor):
    if not actor or not actor.inbox_url or not actor.inbox_api_token:
        return False

    available = (
            not endo_status or
            endo_status == constants.TYPE_TENTATIVE_REJECT
    )
    return available
