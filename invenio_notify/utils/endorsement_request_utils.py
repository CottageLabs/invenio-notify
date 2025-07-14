import uuid
import requests
from flask import current_app

from invenio_notify.records.models import ReviewerModel


def create_endorsement_request_data():
    """Create endorsement request data following COAR notification structure."""
    # KTODO hardcoded for now
    data = {
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
        "object": {
            "id": f"https://127.0.0.1:5000/records/",
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


def send_endorsement_request(reviewer_id):
    """Send endorsement request to a reviewer's inbox.
    
    Args:
        reviewer_id: ID of the reviewer to send request to
        
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

    endorsement_request_data = create_endorsement_request_data()

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

        if response.status_code in {200, 201, 202}:
            return {'is_success': 1, 'message': 'Request Accepted'}, 200
        else:
            # KTODO should not return status code
            return {'is_success': 0, 'message': f'Request failed: {response.status_code}'}, 400

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Failed to send request to reviewer inbox: {e}')
        return {'is_success': 0, 'message': 'Failed to send request'}, 500


def get_available_reviewers():
    """Get list of available reviewers.
    
    Returns:
        list: List of reviewer dictionaries with id and name
    """
    # KTODO implement permission checking
    # KTODO add status name
    # KTODO add available for request

    all_reviewers = ReviewerModel.query.all()
    reviewers = []
    for reviewer in all_reviewers:
        reviewers.append({
            "reviewer_id": reviewer.id,
            "reviewer_name": reviewer.name
        })
    return reviewers