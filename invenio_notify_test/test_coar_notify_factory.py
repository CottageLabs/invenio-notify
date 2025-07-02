from coarnotify.factory import COARNotifyFactory
from invenio_notify_test.fixtures.inbox_fixture import (
    create_inbox_payload__review,
    create_inbox_payload__endorsement_request,
    create_inbox_payload__endorsement_resp,
    create_inbox_payload__tentative_accept,
    create_inbox_payload__reject,
    create_inbox_payload__tentative_reject
)


def test_all_payload_types_compatibility():
    """Test that all create_inbox_payload__ functions work with COARNotifyFactory."""
    record_id = 'test-record'

    payload_functions = [
        create_inbox_payload__review,
        create_inbox_payload__endorsement_request,
        create_inbox_payload__endorsement_resp,
        create_inbox_payload__tentative_accept,
        create_inbox_payload__reject,
        create_inbox_payload__tentative_reject
    ]

    for payload_func in payload_functions:
        print(f"Testing payload function: {payload_func.__name__}")
        raw_payload = payload_func(record_id)

        # Test COARNotifyFactory can process each payload type
        notification = COARNotifyFactory.get_by_object(raw_payload)
        notification_raw = notification.to_jsonld()

        # Verify essential fields are present
        assert 'type' in notification_raw
        assert 'actor' in notification_raw
        assert 'id' in notification_raw
