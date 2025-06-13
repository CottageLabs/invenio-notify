import pytest
import uuid
from invenio_notify.records.models import EndorsementRequestModel
from invenio_notify.services.service import EndorsementRequestService
from invenio_notify.services.config import EndorsementRequestServiceConfig
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer
from invenio_notify_test.utils import BasicDbServiceTestHelper


def create_endorsement_request_service():
    """Create an EndorsementRequestService instance."""
    return EndorsementRequestService(EndorsementRequestServiceConfig)


@pytest.fixture
def create_endorsement_request(superuser_identity, create_reviewer):
    """Fixture to create an endorsement request."""
    def _create_endorsement_request(record_uuid=None, reviewer_id=None, latest_status="Request Endorsement"):
        if reviewer_id is None:
            reviewer = create_reviewer()
            reviewer_id = reviewer.id
        
        if record_uuid is None:
            record_uuid = str(uuid.uuid4())
            
        return EndorsementRequestModel.create({
            'record_uuid': record_uuid,
            'reviewer_id': reviewer_id,
            'raw': {'test': 'data'},
            'latest_status': latest_status
        })
    return _create_endorsement_request


def test_model_create(create_endorsement_request):
    """Test creating an endorsement request model."""
    request = create_endorsement_request()
    assert request.id is not None
    assert request.record_uuid is not None
    assert request.reviewer_id is not None
    assert request.raw == {'test': 'data'}
    assert request.latest_status == "Request Endorsement"


def test_service_create(superuser_identity, create_reviewer):
    """Test creating an endorsement request via service."""
    service = create_endorsement_request_service()
    reviewer = create_reviewer()
    
    data = {
        'record_uuid': str(uuid.uuid4()),
        'reviewer_id': reviewer.id,
        'raw': {'test': 'service_data'},
        'latest_status': 'Request Endorsement'
    }
    
    result = service.create(superuser_identity, data)
    assert result.data['id'] is not None
    assert result.data['record_uuid'] == data['record_uuid']
    assert result.data['reviewer_id'] == data['reviewer_id']


def test_service_update_status(superuser_identity, create_endorsement_request):
    """Test updating endorsement request status via service."""
    service = create_endorsement_request_service()
    request = create_endorsement_request()
    
    result = service.update_status(superuser_identity, request.id, 'Announce Endorsement')
    
    # Verify the status was updated
    updated_request = EndorsementRequestModel.get(request.id)
    assert updated_request.latest_status == 'Announce Endorsement'


def test_service_search_by_record_uuid(superuser_identity, create_endorsement_request):
    """Test searching endorsement requests by record UUID."""
    service = create_endorsement_request_service()
    record_uuid = str(uuid.uuid4())
    
    # Create multiple requests, one with specific record_uuid
    create_endorsement_request()  # unrelated request
    target_request = create_endorsement_request(record_uuid=record_uuid)
    
    # Search by record_uuid
    result = service.search(superuser_identity, params={'q': record_uuid})
    result_list = result.to_dict()['hits']['hits']
    
    assert len(result_list) == 1
    assert result_list[0]['record_uuid'] == record_uuid


class TestEndorsementRequestService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_endorsement_request):
        self.create_endorsement_request = create_endorsement_request

    def _create_service(self):
        return create_endorsement_request_service()

    def _create_record(self, identity):
        return self.create_endorsement_request()