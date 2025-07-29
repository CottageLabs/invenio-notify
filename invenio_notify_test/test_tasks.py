import uuid
from datetime import datetime

from invenio_notify import constants
from invenio_notify.records.models import NotifyInboxModel, EndorsementModel, EndorsementRequestModel, \
    EndorsementReplyModel
from invenio_notify.tasks import inbox_processing, mark_as_processed
from invenio_notify_test.fixtures import inbox_payload
from invenio_notify_test.fixtures.inbox_fixture import create_inbox
from invenio_notify_test.fixtures.inbox_payload import payload_endorsement_resp
from invenio_notify_test.fixtures.inbox_payload import payload_review, \
    payload_reject
from invenio_rdm_records.proxies import current_rdm_records_service


def assert_init_count(n_request=0):
    """Assert initial count of models."""
    assert EndorsementModel.query.count() == 0
    assert EndorsementReplyModel.query.count() == 0
    assert EndorsementRequestModel.query.count() == n_request


def assert_inbox_processed(inbox, process_note_startswith=None):
    """Assert that inbox was processed with expected process_note."""
    updated_inbox = NotifyInboxModel.get(inbox.id)
    assert updated_inbox.process_date is not None
    assert isinstance(updated_inbox.process_date, datetime)

    if process_note_startswith is None:
        assert updated_inbox.process_note is None
    else:
        assert updated_inbox.process_note.startswith(process_note_startswith)


def assert_inbox_processing_failed(inbox, process_note_startswith, n_request=0):
    """Assert that inbox processing failed with expected behavior."""
    # Verify no endorsements exist before processing
    assert_init_count(n_request=n_request)

    # Run the processing task
    inbox_processing()

    assert_inbox_processed(inbox, process_note_startswith=process_note_startswith)

    # Verify no endorsement was created
    assert EndorsementModel.query.count() == 0
    assert EndorsementReplyModel.query.count() == 0


def test_mark_as_processed(db, superuser_identity, create_inbox):
    """Test the mark_as_processed function."""
    # Create a test inbox record
    inbox = create_inbox(recid='r1')

    # Initially, process_date should be None
    assert inbox.process_date is None

    # Mark as processed
    comment = "Test comment"
    mark_as_processed(inbox, comment)
    assert_inbox_processed(inbox, comment)


def test_inbox_processing__success__endorsement(db, rdm_record, inbox_test_data_builder):
    """
    Test successful inbox processing that creates an endorsement.

    Case setting:
    - No Endorsement request
    - type: review
    """
    recid = rdm_record.id
    notification_data = payload_review(recid)

    # Use builder to create test data
    test_data = (inbox_test_data_builder(recid, notification_data)
                 .create_reviewer()
                 .add_member_to_reviewer()
                 .create_inbox())

    # Verify no endorsements exist before processing
    assert_init_count()

    # Run the processing task
    inbox_processing()

    assert_inbox_processed(test_data.inbox)

    # Verify an endorsement was created
    endorsements = EndorsementModel.query.all()
    assert len(endorsements) == 1
    assert EndorsementReplyModel.query.count() == 0

    record = current_rdm_records_service.record_cls.pid.resolve(rdm_record.id)

    # Verify the endorsement has the correct data
    endorsement = endorsements[0]
    assert endorsement.record_id == record.id
    assert endorsement.inbox_id == test_data.inbox.id
    assert endorsement.review_type == constants.TYPE_REVIEW

    # Verify record.endorsements is updated
    assert record.endorsements == [
        {
            'endorsement_count': 0,
            'endorsement_list': [],
            'review_count': 1,
            'reviewer_id': test_data.reviewer.id,
            'reviewer_name': test_data.reviewer.name,
            'review_list': [{
                'created': endorsement.created.isoformat(),
                'url': endorsement.result_url,
            }]
        }
    ]


def test_inbox_processing__success__endorsement_with_endorsement_request(db, rdm_record,
                                                                    inbox_test_data_builder):
    """
    Test that rejection notifications create endorsement replies without endorsements.

    Case setting:
    - Have an Endorsement request
    - type: endorsement response
    """
    recid = rdm_record.id

    # Create a valid working notification but expect it to fail COAR parsing for "Reject" type
    notification_data = payload_endorsement_resp(recid, in_reply_to=inbox_payload.generate_noti_id())

    # Use builder to create test data
    test_data = (inbox_test_data_builder(rdm_record.id, notification_data)
                 .create_reviewer()
                 .add_member_to_reviewer()
                 .create_endorsement_request()
                 .create_inbox())

    inbox = test_data.inbox

    # Verify initial state
    assert_init_count(n_request=1)

    # Run the processing task
    inbox_processing()

    assert_inbox_processed(inbox)
    assert EndorsementModel.query.count() == 1
    assert EndorsementReplyModel.query.count() == 1


def test_inbox_processing__success__reject_with_endorsement_request(db, rdm_record,
                                                                    inbox_test_data_builder):
    """
    Test that rejection notifications create endorsement replies without endorsements.

    Case setting:
    - Have an Endorsement request
    - type: reject
    """
    recid = rdm_record.id

    # Create a valid working notification but expect it to fail COAR parsing for "Reject" type
    notification_data = payload_reject(recid)

    # Use builder to create test data
    test_data = (inbox_test_data_builder(rdm_record.id, notification_data)
                 .create_reviewer()
                 .add_member_to_reviewer()
                 .create_endorsement_request()
                 .create_inbox())

    inbox = test_data.inbox

    # Verify initial state
    assert_init_count(n_request=1)

    # Run the processing task
    inbox_processing()

    assert_inbox_processed(inbox)
    assert EndorsementModel.query.count() == 0
    assert EndorsementReplyModel.query.count() == 1


def test_inbox_processing__fail__reject_without_endorsement_request(db, rdm_record,
                                                                       inbox_test_data_builder):
    """
    Test that rejection notifications create endorsement replies without endorsements.

    Case setting:
    - NO related Endorsement request
    - type: reject
    """
    recid = rdm_record.id

    # Create a valid working notification but expect it to fail COAR parsing for "Reject" type
    notification_data = payload_reject(recid)

    # Even endorsement request is created, but noti_id does not match with new notification data
    test_data = (inbox_test_data_builder(rdm_record.id, notification_data)
                 .create_reviewer()
                 .add_member_to_reviewer()
                 .create_endorsement_request(noti_id=uuid.uuid4())
                 .create_inbox())

    assert_inbox_processing_failed(test_data.inbox,
                                   "Endorsement request not found",
                                   n_request=1)


def test_inbox_processing__fail__record_not_found(db, superuser_identity, create_inbox, create_reviewer,
                                                  inbox_test_data_builder):
    """Test inbox processing when the record is not found."""

    recid = 'r1'
    notification_data = payload_review(recid)
    test_data = (inbox_test_data_builder(recid, notification_data)
                 .create_reviewer()
                 .add_member_to_reviewer()
                 .create_inbox())

    assert_inbox_processing_failed(test_data.inbox, "Failed to resolve record from notification")


def test_inbox_processing__fail__reviewer_not_found(db, rdm_record, inbox_test_data_builder):
    """Test inbox processing when the reviewer is not found."""
    recid = rdm_record.id
    notification_data = payload_review(recid)

    # Do not create reviewer, so actor_id won't match any reviewer
    test_data = (inbox_test_data_builder(recid, notification_data)
                 .create_inbox())

    assert_inbox_processing_failed(test_data.inbox, "Reviewer not found")


def test_inbox_processing__fail__not_a_member(db, rdm_record, inbox_test_data_builder):
    """ Test inbox processing failure when user is not a member of the reviewer."""
    recid = rdm_record.id
    notification_data = payload_review(recid)

    # Create reviewer but do not add user as member
    test_data = (inbox_test_data_builder(recid, notification_data)
                 .create_reviewer()
                 .create_inbox())

    assert_inbox_processing_failed(test_data.inbox, "User is not a member of reviewer")
