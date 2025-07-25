import uuid

from invenio_base import invenio_url_for
from invenio_records_resources.services.records.results import RecordItem

from invenio_notify import constants
from invenio_notify.records.models import ReviewerModel, EndorsementRequestModel, EndorsementModel


def create_endorsement_request_data(user, record: RecordItem, reviewer: ReviewerModel, origin_id: str):
    """Create endorsement request data following COAR notification structure.
    
    Args:
        user: User object making the endorsement request
        reviewer: Reviewer object containing inbox URL and other details
        origin_id: Origin ID from configuration
    """

    # define the object structure
    object = {
        "id": record.data["links"]["self_html"],
        "type": ["Page", "sorg:AboutPage"],
        "ietf:item": {
            "id": record.data["links"]["self_html"],
            "mediaType": "text/html",
            "type": ["Page", "sorg:AboutPage"],
        },
    }

    if 'doi' in record.data['links']:
        object['ietf:cite-as'] = record.data['links']['doi']

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
        "object": object,
        "origin": {
            "id": origin_id,
            "inbox": invenio_url_for('inbox_api.receive_notification'),
            "type": "Service"
        },
        "target": {
            "id": reviewer.actor_id,
            "inbox": reviewer.inbox_url,
            "type": "Service"
        },
        "type": [
            "Offer",
            "coar-notify:EndorsementAction"
        ]
    }

    import pprint
    pprint.pprint(data)
    return data


def get_overall_endorsement_status(record_id, reviewer_id):
    # First check if there's an actual endorsement
    status = get_latest_endorsement_status(record_id, reviewer_id)
    if status:
        return status

    # If no endorsement, check endorsement request status
    status = get_latest_endorsement_request_status(record_id, reviewer_id)
    if status:
        return status

    return None


def get_available_reviewers(record_id):
    """Get list of available reviewers with their endorsement request status.
    
    Args:
        record_id: UUID of the record
        user_id: ID of the user making the request
        
    Returns:
        list: List of reviewer dictionaries with id, name, and status
    """

    all_reviewers = ReviewerModel.query.all()
    reviewers = []

    for reviewer in all_reviewers:
        endo_staus = get_overall_endorsement_status(record_id, reviewer.id)

        # Set status based on endorsement request
        available = can_send(endo_staus, reviewer)

        reviewers.append({
            "reviewer_id": reviewer.id,
            "reviewer_name": reviewer.name,
            "status": endo_staus or 'available',
            'available': available,
        })

    return reviewers


def get_latest_endorsement_request_status(record_id, reviewer_id):
    status = (
        EndorsementRequestModel.query.filter_by(
            record_id=record_id,
            reviewer_id=reviewer_id,
        )
        .order_by(EndorsementRequestModel.created.desc())
        .with_entities(EndorsementRequestModel.latest_status)
        .limit(1)
        .scalar())
    return status


def get_latest_endorsement_status(record_id, reviewer_id):
    status = (
        EndorsementModel.query.filter_by(
            record_id=record_id,
            reviewer_id=reviewer_id,
        )
        .order_by(EndorsementModel.created.desc())
        .with_entities(EndorsementModel.review_type)
        .limit(1)
        .scalar())
    return status


def can_send(endo_status, reviewer):
    if not reviewer or not reviewer.inbox_url or not reviewer.inbox_api_token:
        return False

    available = (
            not endo_status or
            endo_status == constants.TYPE_TENTATIVE_REJECT
    )
    return available
