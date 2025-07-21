import pytest
from coarnotify.factory import COARNotifyFactory
from invenio_notify_test.fixtures.inbox_fixture import (
    create_inbox_payload__review,
    create_inbox_payload__endorsement_request,
    create_inbox_payload__endorsement_resp,
    create_inbox_payload__tentative_accept,
    create_inbox_payload__reject,
    create_inbox_payload__tentative_reject
)


@pytest.mark.parametrize("payload_func", [
    create_inbox_payload__review,
    create_inbox_payload__endorsement_request,
    create_inbox_payload__endorsement_resp,
    create_inbox_payload__tentative_accept,
    create_inbox_payload__reject,
    create_inbox_payload__tentative_reject
], ids=[
    "review",
    "endorsement_request", 
    "endorsement_response",
    "tentative_accept",
    "reject",
    "tentative_reject"
])
def test_payload_type_compatibility(payload_func):
    """Test that create_inbox_payload__ function works with COARNotifyFactory."""
    record_id = 'test-record'
    
    raw_payload = payload_func(record_id)

    # Test COARNotifyFactory can process the payload type
    notification = COARNotifyFactory.get_by_object(raw_payload)
    notification_raw = notification.to_jsonld()

    # Verify essential fields are present
    assert 'type' in notification_raw
    assert 'actor' in notification_raw
    assert 'id' in notification_raw
