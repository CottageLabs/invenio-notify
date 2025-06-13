import uuid

from invenio_notify.proxies import current_endorsement_request_service
from invenio_notify.records.models import EndorsementRequestModel
from invenio_notify_test.fixtures.endorsement_request_fixture import (
    create_endorsement_request,
    create_endorsement_request_data,
)
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer


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
    service = current_endorsement_request_service
    reviewer = create_reviewer()

    data = create_endorsement_request_data(reviewer.id)

    result = service.create(superuser_identity, data)
    assert result.data['id'] is not None
    assert result.data['record_uuid'] == data['record_uuid']
    assert result.data['reviewer_id'] == data['reviewer_id']


def test_service_update_status(superuser_identity, create_endorsement_request):
    """Test updating endorsement request status via service."""
    service = current_endorsement_request_service
    request = create_endorsement_request()

    result = service.update_status(superuser_identity, request.id, 'Announce Endorsement')

    # Verify the status was updated
    updated_request = EndorsementRequestModel.get(request.id)
    assert updated_request.latest_status == 'Announce Endorsement'


def test_service_search_by_record_uuid(superuser_identity, create_endorsement_request):
    """Test searching endorsement requests by record UUID."""
    service = current_endorsement_request_service
    record_uuid = str(uuid.uuid4())

    # Create multiple requests, one with specific record_uuid
    create_endorsement_request()  # unrelated request
    target_request = create_endorsement_request(record_uuid=record_uuid)

    # Search by record_uuid
    result = service.search(superuser_identity, params={'q': record_uuid})
    result_list = result.to_dict()['hits']['hits']

    assert len(result_list) == 1
    assert result_list[0]['record_uuid'] == record_uuid


