import uuid

from invenio_base import invenio_url_for
from invenio_records_resources.services.records.results import RecordItem

from invenio_notify import constants
from invenio_notify.records.models import ReviewerModel, EndorsementRequestModel


def create_endorsement_request_data(user, record: RecordItem, reviewer: ReviewerModel):
    """Create endorsement request data following COAR notification structure.
    
    Args:
        user: User object making the endorsement request
        reviewer: Reviewer object containing inbox URL and other details
    """

    # KTODO which value should be used for `origin.id`? --- config
    # KTODO update it to only attach HTML link to the object

    # define the object structure
    object = {
        "id": record.data["links"]["self_html"],
        "type": ["Page", "sorg:AboutPage"]
    }

    if 'doi' in record.data['links']:
        object['ietf:cite-as'] = record.data['links']['doi']

    if 'files' in record.data and record.data:

        # they have two versions to get file objects
        record_files = record.data['files']
        if isinstance(record_files, list):
            files = record_files
        else:
            files = record_files.get('entries', {}).values()

        for file in files:
            link = file.get('links', {}).get('self')
            if not link:
                continue

            is_pdf = file['key'].endswith('.pdf') or '.pdf' in link
            if is_pdf:
                object['ietf:item'] = {
                    "id": link,
                    "mediaType": "application/pdf",
                    "type": ["Article", "sorg:ScholarlyArticle"],
                }
                break

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
            "id": invenio_url_for('inbox_api.receive_notification'),
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


def get_available_reviewers(record_id, user_id):
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
        endorsement_request = get_latest_endorsement_request(record_id, reviewer.id, user_id)

        # Set status based on endorsement request
        if endorsement_request:
            status = endorsement_request.latest_status
        else:
            status = 'available'

        available = can_send(endorsement_request, reviewer)

        reviewers.append({
            "reviewer_id": reviewer.id,
            "reviewer_name": reviewer.name,
            "status": status,
            'available': available,
        })

    return reviewers


def get_latest_endorsement_request(record_id, reviewer_id, user_id):
    endorsement_request = EndorsementRequestModel.query.filter_by(
        record_id=record_id,
        reviewer_id=reviewer_id,
        user_id=user_id
    ).order_by(EndorsementRequestModel.created.desc()).first()
    return endorsement_request


def can_send(endorsement_request, reviewer):
    if not reviewer or not reviewer.inbox_url or not reviewer.inbox_api_token:
        return False

    available = (
            not endorsement_request or
            endorsement_request.latest_status == constants.TYPE_TENTATIVE_REJECT
    )
    return available
