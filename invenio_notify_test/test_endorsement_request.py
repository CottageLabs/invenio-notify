import uuid

from invenio_notify.proxies import current_endorsement_request_service
from invenio_notify.records.models import EndorsementRequestModel
from invenio_notify_test.conftest import prepare_test_rdm_record
from invenio_notify_test.fixtures.endorsement_request_fixture import (
    create_endorsement_request,
    create_endorsement_request_data,
)
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer


def test_model_create(create_endorsement_request, superuser_identity):
    """Test creating an endorsement request model."""
    request = create_endorsement_request()
    assert request.id is not None
    assert request.record_id is not None
    assert request.reviewer_id is not None
    assert request.user_id == superuser_identity.id
    assert request.raw == {'test': 'data'}
    assert request.latest_status == "Request Endorsement"


def test_service_create(superuser_identity, create_reviewer, db, minimal_record):
    """Test creating an endorsement request via service."""
    service = current_endorsement_request_service
    reviewer = create_reviewer()

    test_record = prepare_test_rdm_record(db, minimal_record)
    data = create_endorsement_request_data(reviewer.id, test_record.id)

    result = service.create(superuser_identity, data)
    assert result.data['id'] is not None
    assert result.data['record_id'] == data['record_id']
    assert result.data['reviewer_id'] == data['reviewer_id']
    assert result.data['user_id'] == superuser_identity.id


def test_service_update_status(superuser_identity, create_endorsement_request):
    """Test updating endorsement request status via service."""
    service = current_endorsement_request_service
    request = create_endorsement_request()

    result = service.update_status(superuser_identity, request.id, 'Announce Endorsement')

    # Verify the status was updated
    updated_request = EndorsementRequestModel.get(request.id)
    assert updated_request.latest_status == 'Announce Endorsement'


def test_service_search_by_record_id(superuser_identity, create_endorsement_request, db, minimal_record):
    """Test searching endorsement requests by record ID."""
    service = current_endorsement_request_service
    
    # Create a test record and use its ID
    test_record = prepare_test_rdm_record(db, minimal_record)
    record_id = test_record.id

    # Create multiple requests, one with specific record_id
    create_endorsement_request()  # unrelated request
    target_request = create_endorsement_request(record_id=record_id)

    # Search by record_id
    result = service.search(superuser_identity, params={'q': str(record_id)})
    result_list = result.to_dict()['hits']['hits']

    assert len(result_list) == 1
    assert result_list[0]['record_id'] == str(record_id)


def test_service_create_auto_set_user_id(superuser_identity, create_reviewer, db, minimal_record):
    """Test that service auto-sets user_id when not provided."""
    service = current_endorsement_request_service
    reviewer = create_reviewer()

    # Create data without user_id, but with valid record_id
    test_record = prepare_test_rdm_record(db, minimal_record)
    data = create_endorsement_request_data(reviewer.id, test_record.id)
    assert 'user_id' not in data

    result = service.create(superuser_identity, data)
    assert result.data['user_id'] == superuser_identity.id


def test_service_create_preserve_explicit_user_id(superuser_identity, create_reviewer, db, minimal_record):
    """Test that service preserves explicitly provided user_id."""
    service = current_endorsement_request_service
    reviewer = create_reviewer()

    # Create data with explicit user_id (use superuser_identity.id as a valid user_id)
    test_record = prepare_test_rdm_record(db, minimal_record)
    explicit_user_id = superuser_identity.id
    data = create_endorsement_request_data(reviewer.id, test_record.id, user_id=explicit_user_id)
    assert data['user_id'] == explicit_user_id

    result = service.create(superuser_identity, data)
    assert result.data['user_id'] == explicit_user_id


