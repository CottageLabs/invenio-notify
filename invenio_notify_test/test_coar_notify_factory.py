import pytest

from coarnotify.factory import COARNotifyFactory
from invenio_notify_test.fixtures.endorsement_request_payload import payload_endorsement_request
from invenio_notify_test.fixtures.inbox_payload import (
    payload_review,
    payload_endorsement_resp,
    payload_tentative_accept,
    payload_reject,
    payload_tentative_reject
)


@pytest.mark.parametrize("payload_func", [
    payload_review,
    payload_endorsement_request,
    payload_endorsement_resp,
    payload_tentative_accept,
    payload_reject,
    payload_tentative_reject
], ids=[
    "review",
    "endorsement_request", 
    "endorsement_response",
    "tentative_accept",
    "reject",
    "tentative_reject"
])
def test_payload_type_compatibility(payload_func):
    """Test that payload_ functions work with COARNotifyFactory."""
    record_id = 'test-record'
    
    raw_payload = payload_func(record_id)

    # Test COARNotifyFactory can process the payload type
    notification = COARNotifyFactory.get_by_object(raw_payload)
    notification_raw = notification.to_jsonld()

    # Verify essential fields are present
    assert 'type' in notification_raw
    assert 'actor' in notification_raw
    assert 'id' in notification_raw
