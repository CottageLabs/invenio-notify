import uuid

from invenio_records_resources.services.records.results import RecordItem

from invenio_notify import constants
from invenio_notify.records.models import ReviewerModel, EndorsementRequestModel


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
