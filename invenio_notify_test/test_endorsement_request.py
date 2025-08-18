import uuid

from invenio_notify.records.models import EndorsementRequestModel
from invenio_notify_test.fixtures.endorsement_request_fixture import (
    create_endorsement_request,
)


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


def test_model_create_with_noti_id(create_endorsement_request, superuser_identity):
    """Test creating an endorsement request model with noti_id."""
    test_noti_id = uuid.uuid4()
    request = create_endorsement_request(noti_id=test_noti_id)
    assert request.id is not None
    assert request.noti_id == test_noti_id


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
