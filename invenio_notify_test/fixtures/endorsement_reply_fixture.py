import pytest

from invenio_notify.records.models import EndorsementReplyModel, EndorsementRequestModel
from invenio_notify_test.fixtures.endorsement_request_fixture import create_endorsement_request_data


@pytest.fixture
def create_endorsement_reply(superuser_identity, create_reviewer, create_inbox):
    """Fixture to create an endorsement reply."""
    def _create_endorsement_reply(endorsement_request_id=None, status="Request Endorsement", with_endorsement=False):
        if endorsement_request_id is None:
            # Create an endorsement request
            reviewer = create_reviewer()
            request = EndorsementRequestModel.create(
                create_endorsement_request_data(reviewer.id)
            )
            endorsement_request_id = request.id
        
        inbox = create_inbox()
        endorsement_id = None
        
        if with_endorsement:
            # For simplicity, just use a dummy endorsement_id
            endorsement_id = 999
        
        return EndorsementReplyModel.create({
            'endorsement_request_id': endorsement_request_id,
            'inbox_id': inbox.id,
            'endorsement_id': endorsement_id,
            'status': status
        })
    return _create_endorsement_reply