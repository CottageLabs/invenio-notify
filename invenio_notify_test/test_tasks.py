import json
from datetime import datetime
from invenio_rdm_records.proxies import current_rdm_records

from invenio_notify import constants
from invenio_notify.records.models import NotifyInboxModel, EndorsementMetadataModel
from invenio_notify.tasks import inbox_processing, mark_as_processed
from inbox_fixture import create_notification_data
from invenio_notify_test.inbox_fixture import create_inbox


def test_mark_as_processed(db, superuser_identity, create_inbox):
    """Test the mark_as_processed function."""
    # Create a test inbox record
    inbox = create_inbox(recid='r1')

    # Initially, process_date should be None
    assert inbox.process_date is None

    # Mark as processed
    mark_as_processed(inbox, "Test comment")

    inbox = NotifyInboxModel.query.get(inbox.id)
    assert inbox.process_date is not None
    assert isinstance(inbox.process_date, datetime)


def test_inbox_processing_success(db, rdm_record, superuser_identity):
    """Test successful inbox processing that creates an endorsement."""
    recid = rdm_record.id

    notification_data = create_notification_data(recid)

    # Create inbox record with real notification data
    inbox = NotifyInboxModel.create({
        'raw': json.dumps(notification_data),
        'recid': recid,
        'user_id': superuser_identity.id,
    })

    # Verify no endorsements exist before processing
    assert EndorsementMetadataModel.query.count() == 0

    # Run the processing task
    inbox_processing()

    # Refresh the inbox record from DB
    updated_inbox = NotifyInboxModel.get(inbox.id)

    # Check that the inbox record was marked as processed
    assert updated_inbox.process_date is not None

    # Verify an endorsement was created
    endorsements = EndorsementMetadataModel.query.all()
    assert len(endorsements) == 1

    # Verify the endorsement has the correct data
    endorsement = endorsements[0]
    assert endorsement.record_id == current_rdm_records.records_service.record_cls.pid.resolve(rdm_record.id).id
    assert endorsement.user_id == superuser_identity.id
    assert endorsement.inbox_id == inbox.id
    assert endorsement.review_type == constants.TYPE_REVIEW


def test_inbox_processing_record_not_found(db, superuser_identity, create_inbox):
    """Test inbox processing when the record is not found."""

    recid = 'r1'

    notification_data = create_notification_data(recid)

    # Create inbox record with notification pointing to non-existent record
    inbox = create_inbox(
        recid=recid,
        raw=json.dumps(notification_data)
    )

    # Verify no endorsements exist before processing
    assert EndorsementMetadataModel.query.count() == 0

    # Run the processing task
    inbox_processing()

    # Refresh the inbox record from DB
    updated_inbox = NotifyInboxModel.get(inbox.id)

    # Check that the inbox record was marked as processed
    assert updated_inbox.process_date is not None
    assert updated_inbox.process_note is not None

    # Verify no endorsement was created
    assert EndorsementMetadataModel.query.count() == 0
