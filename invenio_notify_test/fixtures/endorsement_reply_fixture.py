import pytest

from invenio_notify.records.models import EndorsementReplyModel, EndorsementRequestModel
from invenio_notify_test.fixtures.endorsement_request_fixture import create_endorsement_request


@pytest.fixture
def create_endorsement_reply(superuser_identity, create_reviewer, create_inbox, create_endorsement_request):
    """Fixture to create an endorsement reply."""
    def _create_endorsement_reply(endorsement_request_id=None, status="Request Endorsement"):
        if endorsement_request_id is None:
            # Create an endorsement request
            reviewer = create_reviewer()
            request = create_endorsement_request(reviewer_id=reviewer.id)
            endorsement_request_id = request.id
        
        inbox = create_inbox()
        
        return EndorsementReplyModel.create({
            'endorsement_request_id': endorsement_request_id,
            'inbox_id': inbox.id,
            'status': status
        })
    return _create_endorsement_reply