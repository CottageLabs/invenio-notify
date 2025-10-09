from tests.builders.inbox_test_data_builder import inbox_test_data_builder
from tests.fixtures.inbox_payload import payload_reject
from invenio_rdm_records.proxies import current_rdm_records


def test_inbox_test_data_builder(db, rdm_record, superuser_identity, inbox_test_data_builder):
    """Test the InboxTestDataBuilder creates all components correctly."""
    record_id = rdm_record.id
    
    # Create test notification data
    notification_data = payload_reject(record_id)
    
    # Use the builder
    builder = (inbox_test_data_builder(rdm_record.id, notification_data, superuser_identity)
               .create_actor()
               .add_member_to_actor()
               .create_endorsement_request()
               .create_inbox()
               )
    
    # Verify all components were created
    assert builder.actor is not None
    assert builder.actor.actor_id == notification_data['actor']['id']
    
    assert builder.endorsement_request is not None
    record = current_rdm_records.records_service.record_cls.pid.resolve(rdm_record.id)
    assert builder.endorsement_request.record_id == record.id
    assert builder.endorsement_request.actor_id == builder.actor.id
    assert builder.endorsement_request.notification_id == notification_data['inReplyTo']
    
    assert builder.inbox is not None
    assert builder.inbox.record_id == record_id
    assert builder.inbox.raw == notification_data
    assert builder.inbox.notification_id == notification_data.get('id')


def test_inbox_test_data_builder_usage_example(db, rdm_record, superuser_identity, inbox_test_data_builder):
    """Example showing how to use the InboxTestDataBuilder like in the original test."""
    record_id = rdm_record.id
    notification_data = payload_reject(record_id)

    
    # NEW pattern - AFTER using builder:
    test_data = (inbox_test_data_builder(rdm_record.id, notification_data, superuser_identity)
                 .create_actor()
                 .add_member_to_actor()
                 .create_endorsement_request()
                 .create_inbox())
    
    # Access the created components
    actor = test_data.actor
    endorsement_request = test_data.endorsement_request
    inbox = test_data.inbox
    
    # Verify they match the original pattern
    assert actor.actor_id == notification_data['actor']['id']
    assert endorsement_request.actor_id == actor.id
    assert endorsement_request.notification_id == notification_data['inReplyTo']
    assert inbox.record_id == record_id
    assert inbox.raw == notification_data