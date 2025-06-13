import uuid

import pytest

from invenio_notify.records.models import EndorsementReplyModel, EndorsementRequestModel
from invenio_notify.proxies import current_endorsement_reply_service
from invenio_notify_test.fixtures.inbox_fixture import create_inbox
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer
from invenio_notify_test.utils import BasicDbServiceTestHelper


def create_default_endorsement_request_data(reviewer_id, record_uuid=None, latest_status="Request Endorsement"):
    """Create default data for EndorsementRequestModel.
    
    Args:
        reviewer_id: ID of the reviewer
        record_uuid: UUID of the record (generates random if None)
        latest_status: Status of the request
        
    Returns:
        dict: Data for creating EndorsementRequestModel
    """
    return {
        'record_uuid': record_uuid or str(uuid.uuid4()),
        'reviewer_id': reviewer_id,
        'raw': {'test': 'data'},
        'latest_status': latest_status
    }


def create_endorsement_reply_service():
    """Create an EndorsementReplyService instance."""
    return current_endorsement_reply_service


@pytest.fixture
def create_endorsement_reply(superuser_identity, create_reviewer, create_inbox):
    """Fixture to create an endorsement reply."""
    def _create_endorsement_reply(endorsement_request_id=None, status="Request Endorsement", with_endorsement=False):
        if endorsement_request_id is None:
            # Create an endorsement request
            reviewer = create_reviewer()
            request = EndorsementRequestModel.create(
                create_default_endorsement_request_data(reviewer.id)
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


def test_model_create(create_endorsement_reply):
    """Test creating an endorsement reply model."""
    reply = create_endorsement_reply()
    assert reply.id is not None
    assert reply.endorsement_request_id is not None
    assert reply.inbox_id is not None
    assert reply.endorsement_id is None  # No endorsement by default
    assert reply.status == "Request Endorsement"


def test_service_create(superuser_identity, create_reviewer, create_inbox):
    """Test creating an endorsement reply via service."""
    service = create_endorsement_reply_service()
    
    # Create dependencies
    reviewer = create_reviewer()
    request = EndorsementRequestModel.create(
        create_default_endorsement_request_data(reviewer.id)
    )
    inbox = create_inbox()
    
    data = {
        'endorsement_request_id': request.id,
        'inbox_id': inbox.id,
        'status': 'Announce Endorsement'
    }
    
    result = service.create(superuser_identity, data)
    assert result.data['id'] is not None
    assert result.data['endorsement_request_id'] == data['endorsement_request_id']
    assert result.data['status'] == data['status']
    assert result.data['endorsement_id'] is None
    
    # Verify that the parent request status was updated
    updated_request = EndorsementRequestModel.get(request.id)
    assert updated_request.latest_status == 'Announce Endorsement'


def test_service_create_without_endorsement(superuser_identity, create_reviewer, create_inbox):
    """Test creating an endorsement reply without endorsement_id."""
    service = create_endorsement_reply_service()
    
    # Create dependencies
    reviewer = create_reviewer()
    request = EndorsementRequestModel.create(
        create_default_endorsement_request_data(reviewer.id)
    )
    inbox = create_inbox()
    
    data = {
        'endorsement_request_id': request.id,
        'inbox_id': inbox.id,
        'status': 'Reject'
    }
    
    result = service.create(superuser_identity, data)
    assert result.data['id'] is not None
    assert result.data['endorsement_id'] is None
    assert result.data['status'] == 'Reject'


def test_service_search_by_request_id(superuser_identity, create_endorsement_reply):
    """Test searching endorsement replies by endorsement request ID."""
    service = create_endorsement_reply_service()
    
    # Create replies for different requests
    reply1 = create_endorsement_reply()
    reply2 = create_endorsement_reply()  # different request
    reply3 = create_endorsement_reply(endorsement_request_id=reply1.endorsement_request_id)  # same request as reply1
    
    # Search by endorsement_request_id
    result = service.search(superuser_identity, params={'q': str(reply1.endorsement_request_id)})
    result_list = result.to_dict()['hits']['hits']
    
    # Should find reply1 and reply3 (both have same endorsement_request_id)
    assert len(result_list) == 2
    found_ids = {int(r['id']) for r in result_list}
    assert reply1.id in found_ids
    assert reply3.id in found_ids
    assert reply2.id not in found_ids


class TestEndorsementReplyService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_endorsement_reply):
        self.create_endorsement_reply = create_endorsement_reply

    def _create_service(self):
        return create_endorsement_reply_service()

    def _create_record(self, identity):
        return self.create_endorsement_reply()