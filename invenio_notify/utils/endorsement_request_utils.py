import uuid

import requests
from flask import current_app
from invenio_db.uow import unit_of_work
from invenio_records_resources.services.records.results import RecordItem

from invenio_notify import constants
from invenio_notify.records.models import ReviewerModel, EndorsementRequestModel
from invenio_rdm_records.records import RDMRecord


def create_endorsement_request_data(user, record: RecordItem):
    """Create endorsement request data following COAR notification structure.
    
    Args:
        user: User object making the endorsement request
    """
    # KTODO add test cases
    # KTODO hardcoded for now

    # KTODO define how to fill-in the value of `object`
    # KTODO fill-in value origin
    # KTODO fill-in value target

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
        "object": {
            "id": record.data["links"]["self_html"],
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
    return data


@unit_of_work()
def send_endorsement_request(reviewer_id, record: RecordItem, user, uow=None):
    """Send endorsement request to a reviewer's inbox.
    
    Args:
        reviewer_id: ID of the reviewer to send request to
        record: The record object
        user: User object making the request
        
    Returns:
        tuple: (response_dict, status_code)
    """

    try:
        reviewer = ReviewerModel.get(reviewer_id)
    except Exception:
        return {'is_success': 0, 'message': 'Reviewer not found'}, 404

    if not reviewer.inbox_url or not reviewer.inbox_url.startswith('http'):
        current_app.logger.error(
            f'Reviewer inbox URL is not configured for reviewer {reviewer_id} url[{reviewer.inbox_url}]'
        )
        return {'is_success': 0, 'message': 'Reviewer inbox URL not configured'}, 400

    endorsement_request_data = create_endorsement_request_data(user, record)

    try:
        response = requests.post(
            reviewer.inbox_url,
            json=endorsement_request_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {reviewer.inbox_api_token}',
            },
            timeout=30
        )

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Failed to send request to reviewer inbox: {e}')
        return {'is_success': 0, 'message': 'Failed to send request'}, 500

    if response.status_code not in {200, 201, 202}:
        # KTODO should not return status code
        return {'is_success': 0, 'message': f'Request failed: {response.status_code}'}, 400

    # Create endorsement request record
    try:
        EndorsementRequestModel.create({
            "noti_id": endorsement_request_data["id"],
            "record_id": record._record.model.id,
            "user_id": user.id,
            "reviewer_id": reviewer_id,
            "raw": endorsement_request_data,
            "latest_status": constants.STATUS_REQUEST_ENDORSEMENT,
        })
        current_app.logger.info(f'Created endorsement request record for reviewer {reviewer_id}')
    except Exception as e:
        current_app.logger.error(f'Failed to create endorsement request record: {e}')
        return {'is_success': 0, 'message': 'Failed to create endorsement request record'}, 500

    return {'is_success': 1, 'message': 'Request Accepted'}, 200


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
        # Find the latest endorsement request for this reviewer and record
        endorsement_request = EndorsementRequestModel.query.filter_by(
            record_id=record_id,
            reviewer_id=reviewer.id,
            user_id=user_id
        ).order_by(EndorsementRequestModel.created.desc()).first()

        # Set status based on endorsement request
        if endorsement_request:
            status = endorsement_request.latest_status
        else:
            status = 'available'

        available = (
                not endorsement_request or
                endorsement_request.latest_status == constants.TYPE_TENTATIVE_REJECT
        )

        reviewers.append({
            "reviewer_id": reviewer.id,
            "reviewer_name": reviewer.name,
            "status": status,
            'available': available,
        })

    return reviewers
