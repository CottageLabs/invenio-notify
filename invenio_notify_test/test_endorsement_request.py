import uuid

from invenio_notify.proxies import current_endorsement_request_service
from invenio_notify.records.models import EndorsementRequestModel
from invenio_notify_test.fixtures.endorsement_request_fixture import (
    create_endorsement_request,
    create_endorsement_request_data,
)
from invenio_notify_test.fixtures.record_fixture import prepare_test_rdm_record
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
    assert request.noti_id is not None
    assert isinstance(request.noti_id, (str, type(request.noti_id)))


def test_service_create(superuser_identity, create_reviewer, db, minimal_record):
    """Test creating an endorsement request via service."""
    reviewer = create_reviewer()

    test_record = prepare_test_rdm_record(db, minimal_record)
    data = create_endorsement_request_data(reviewer.id, test_record.id)

    result = current_endorsement_request_service.create(superuser_identity, data)
    assert result.data['id'] is not None
    assert result.data['record_id'] == data['record_id']
    assert result.data['reviewer_id'] == data['reviewer_id']
    assert result.data['user_id'] == superuser_identity.id


def test_service_update_status(superuser_identity, create_endorsement_request):
    """Test updating endorsement request status via service."""
    request = create_endorsement_request()

    result = current_endorsement_request_service.update_status(superuser_identity, request.id, 'Announce Endorsement')

    # Verify the status was updated
    updated_request = EndorsementRequestModel.get(request.id)
    assert updated_request.latest_status == 'Announce Endorsement'


def test_service_search_by_record_id(superuser_identity, create_endorsement_request, db, minimal_record):
    """Test searching endorsement requests by record ID."""
    # Create a test record and use its ID
    test_record = prepare_test_rdm_record(db, minimal_record)
    record_id = test_record.id

    # Create multiple requests, one with specific record_id
    create_endorsement_request()  # unrelated request
    target_request = create_endorsement_request(record_id=record_id)

    # Search by record_id
    result = current_endorsement_request_service.search(superuser_identity, params={'q': str(record_id)})
    result_list = result.to_dict()['hits']['hits']

    assert len(result_list) == 1
    assert result_list[0]['record_id'] == str(record_id)


def test_service_create_auto_set_user_id(superuser_identity, create_reviewer, db, minimal_record):
    """Test that service auto-sets user_id when not provided."""
    reviewer = create_reviewer()

    # Create data without user_id, but with valid record_id
    test_record = prepare_test_rdm_record(db, minimal_record)
    data = create_endorsement_request_data(reviewer.id, test_record.id)
    assert 'user_id' not in data

    result = current_endorsement_request_service.create(superuser_identity, data)
    assert result.data['user_id'] == superuser_identity.id


def test_service_create_preserve_explicit_user_id(superuser_identity, create_reviewer, db, minimal_record):
    """Test that service preserves explicitly provided user_id."""
    reviewer = create_reviewer()

    # Create data with explicit user_id (use superuser_identity.id as a valid user_id)
    test_record = prepare_test_rdm_record(db, minimal_record)
    explicit_user_id = superuser_identity.id
    data = create_endorsement_request_data(reviewer.id, test_record.id, user_id=explicit_user_id)
    assert data['user_id'] == explicit_user_id

    result = current_endorsement_request_service.create(superuser_identity, data)
    assert result.data['user_id'] == explicit_user_id


def test_model_create_with_noti_id(create_endorsement_request, superuser_identity):
    """Test creating an endorsement request model with noti_id."""
    test_noti_id = uuid.uuid4()
    request = create_endorsement_request(noti_id=test_noti_id)
    assert request.id is not None
    assert request.noti_id == test_noti_id


def test_service_create_with_noti_id(superuser_identity, create_reviewer, db, minimal_record):
    """Test creating an endorsement request via service with noti_id."""
    reviewer = create_reviewer()

    test_record = prepare_test_rdm_record(db, minimal_record)
    test_noti_id = uuid.uuid4()
    data = create_endorsement_request_data(reviewer.id, test_record.id, noti_id=test_noti_id)

    result = current_endorsement_request_service.create(superuser_identity, data)
    assert str(result.data['noti_id']) == str(test_noti_id)


def test_noti_id_uniqueness(create_endorsement_request):
    """Test that noti_id must be unique."""
    import pytest
    from sqlalchemy.exc import IntegrityError

    test_noti_id = uuid.uuid4()

    # Create first request with specific noti_id
    create_endorsement_request(noti_id=test_noti_id)

    # Try to create second request with same noti_id - should fail
    with pytest.raises(IntegrityError):
        create_endorsement_request(noti_id=test_noti_id)
        EndorsementRequestModel.commit()
