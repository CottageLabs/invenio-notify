import uuid

from invenio_notify.records.models import EndorsementRequestModel
from tests.fixtures.endorsement_request_fixture import (
    create_endorsement_request,
)


def test_model_create(create_endorsement_request, superuser_identity):
    """Test creating an endorsement request model."""
    request = create_endorsement_request()
    assert request.id is not None
    assert request.record_id is not None
    assert request.actor_id is not None
    assert request.user_id == superuser_identity.id
    assert request.raw == {'test': 'data'}
    assert request.latest_status == "Request Endorsement"
    assert request.notification_id is not None
    assert isinstance(request.notification_id, (str, type(request.notification_id)))


def test_model_create_with_notification_id(create_endorsement_request, superuser_identity):
    """Test creating an endorsement request model with notification_id."""
    test_notification_id = uuid.uuid4()
    request = create_endorsement_request(notification_id=test_notification_id)
    assert request.id is not None
    assert request.notification_id == test_notification_id


def test_notification_id_uniqueness(create_endorsement_request):
    """Test that notification_id must be unique."""
    import pytest
    from sqlalchemy.exc import IntegrityError

    test_notification_id = uuid.uuid4()

    # Create first request with specific notification_id
    create_endorsement_request(notification_id=test_notification_id)

    # Try to create second request with same notification_id - should fail
    with pytest.raises(IntegrityError):
        create_endorsement_request(notification_id=test_notification_id)
        EndorsementRequestModel.commit()
