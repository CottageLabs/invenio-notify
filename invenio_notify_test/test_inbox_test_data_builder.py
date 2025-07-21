from invenio_notify_test.builders.inbox_test_data_builder import inbox_test_data_builder
from invenio_notify_test.fixtures.inbox_fixture import create_inbox_payload__reject
from invenio_rdm_records.proxies import current_rdm_records


def test_inbox_test_data_builder(db, rdm_record, superuser_identity, inbox_test_data_builder):
    """Test the InboxTestDataBuilder creates all components correctly."""
    recid = rdm_record.id
    
    # Create test notification data
    notification_data = create_inbox_payload__reject(recid)
    
    # Use the builder
    builder = (inbox_test_data_builder(rdm_record.id, notification_data, superuser_identity)
               .create_reviewer()
               .add_member_to_reviewer()
               .create_endorsement_request()
               .create_inbox()
               )
    
    # Verify all components were created
    assert builder.reviewer is not None
    assert builder.reviewer.actor_id == notification_data['actor']['id']
    
    assert builder.endorsement_request is not None
    record = current_rdm_records.records_service.record_cls.pid.resolve(rdm_record.id)
    assert builder.endorsement_request.record_id == record.id
    assert builder.endorsement_request.reviewer_id == builder.reviewer.id
    assert builder.endorsement_request.noti_id == notification_data['inReplyTo']
    
    assert builder.inbox is not None
    assert builder.inbox.recid == recid
    assert builder.inbox.raw == notification_data
    assert builder.inbox.noti_id == notification_data.get('id')


def test_inbox_test_data_builder_usage_example(db, rdm_record, superuser_identity, inbox_test_data_builder):
    """Example showing how to use the InboxTestDataBuilder like in the original test."""
    recid = rdm_record.id
    notification_data = create_inbox_payload__reject(recid)

    
    # NEW pattern - AFTER using builder:
    test_data = (inbox_test_data_builder(rdm_record.id, notification_data, superuser_identity)
                 .create_reviewer()
                 .add_member_to_reviewer()
                 .create_endorsement_request()
                 .create_inbox())
    
    # Access the created components
    reviewer = test_data.reviewer
    endorsement_request = test_data.endorsement_request
    inbox = test_data.inbox
    
    # Verify they match the original pattern
    assert reviewer.actor_id == notification_data['actor']['id']
    assert endorsement_request.reviewer_id == reviewer.id
    assert endorsement_request.noti_id == notification_data['inReplyTo']
    assert inbox.recid == recid
    assert inbox.raw == notification_data