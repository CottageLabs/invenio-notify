from datetime import datetime

from invenio_notify import constants
from invenio_notify.records.models import NotifyInboxModel, EndorsementModel, EndorsementRequestModel, \
    EndorsementReplyModel
from invenio_notify.tasks import inbox_processing, mark_as_processed
from invenio_notify.utils import reviewer_utils
from invenio_notify_test.fixtures.inbox_fixture import create_inbox
from invenio_notify_test.fixtures.inbox_fixture import create_inbox_payload__review, create_inbox_payload__reject
from invenio_rdm_records.proxies import current_rdm_records


def assert_inbox_processed(inbox, process_note_startswith=None):
    """Assert that inbox was processed with expected process_note."""
    updated_inbox = NotifyInboxModel.get(inbox.id)
    assert updated_inbox.process_date is not None
    assert isinstance(updated_inbox.process_date, datetime)

    if process_note_startswith is None:
        assert updated_inbox.process_note is None
    else:
        assert updated_inbox.process_note.startswith(process_note_startswith)


def assert_inbox_processing_failed(inbox, process_note_startswith):
    """Assert that inbox processing failed with expected behavior."""
    # Verify no endorsements exist before processing
    assert EndorsementModel.query.count() == 0
    assert EndorsementReplyModel.query.count() == 0

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


def test_inbox_processing__success__endorsement(db, rdm_record, superuser_identity, create_reviewer, create_inbox):
    """
    Test successful inbox processing that creates an endorsement.

    Case setting:
    - No Endorsement request
    - type: review
    """
    recid = rdm_record.id

    notification_data = create_inbox_payload__review(recid)

    # add sender account to reviewer members
    reviewer = create_reviewer(actor_id=notification_data['actor']['id'])
    reviewer_utils.add_member_to_reviewer(reviewer.id, superuser_identity.id, )

    # Create inbox record with real notification data
    inbox = create_inbox(
        recid=recid,
        raw=notification_data
    )

    # Verify no endorsements exist before processing
    assert EndorsementModel.query.count() == 0
    assert EndorsementReplyModel.query.count() == 0
    assert EndorsementRequestModel.query.count() == 0

    # Run the processing task
    inbox_processing()

    assert_inbox_processed(inbox)

    # Verify an endorsement was created
    endorsements = EndorsementModel.query.all()
    assert len(endorsements) == 1
    assert EndorsementReplyModel.query.count() == 0

    record = current_rdm_records.records_service.record_cls.pid.resolve(rdm_record.id)

    # Verify the endorsement has the correct data
    endorsement = endorsements[0]
    assert endorsement.record_id == record.id
    assert endorsement.inbox_id == inbox.id
    assert endorsement.review_type == constants.TYPE_REVIEW

    # Verify record.endorsements is updated
    assert record.endorsements == [
        {
            'endorsement_count': 0,
            'endorsement_list': [],
            'review_count': 1,
            'reviewer_id': reviewer.id,
            'reviewer_name': reviewer.name,
            'review_list': [{
                'created': endorsement.created.isoformat(),
                'url': endorsement.result_url,
            }]
        }
    ]


def test_inbox_processing__success__reject_with_endorsement_request(db, rdm_record, superuser_identity, create_inbox,
                                                                    create_reviewer, create_endorsement_request):
    """Test that rejection notifications create endorsement replies without endorsements."""
    # KTODO review this test logic
    recid = rdm_record.id

    # Resolve record to get its UUID
    record = current_rdm_records.records_service.record_cls.pid.resolve(rdm_record.id)

    # Create a valid working notification but expect it to fail COAR parsing for "Reject" type
    import uuid
    request_uuid = uuid.uuid4()
    notification_data = create_inbox_payload__reject(recid, in_reply_to=request_uuid)

    # Create reviewer matching the actor in notification
    reviewer = create_reviewer(actor_id=notification_data['actor']['id'])
    reviewer_utils.add_member_to_reviewer(reviewer.id, superuser_identity.id, )

    # Create an endorsement request first with the same noti_id as inReplyTo
    endorsement_request = create_endorsement_request(
        record_id=record.id,
        reviewer_id=reviewer.id,
        user_id=superuser_identity.id,
        noti_id=request_uuid
    )

    # Create inbox record with rejection notification
    inbox = create_inbox(
        recid=recid,
        raw=notification_data
    )

    # Verify initial state
    assert EndorsementModel.query.count() == 0
    assert EndorsementReplyModel.query.count() == 0
    assert EndorsementRequestModel.query.count() == 1

    # Run the processing task
    inbox_processing()

    assert_inbox_processed(inbox)

    assert EndorsementModel.query.count() == 0
    assert EndorsementReplyModel.query.count() == 1


def test_inbox_processing__fail__record_not_found(db, superuser_identity, create_inbox, create_reviewer):
    """Test inbox processing when the record is not found."""

    recid = 'r1'

    notification_data = create_inbox_payload__review(recid)

    # Create reviewer so we pass the reviewer check and reach the record resolution failure
    reviewer = create_reviewer(actor_id=notification_data['actor']['id'])
    reviewer_utils.add_member_to_reviewer(reviewer.id, superuser_identity.id, )

    # Create inbox record with notification pointing to non-existent record
    inbox = create_inbox(
        recid=recid,
        raw=notification_data
    )

    assert_inbox_processing_failed(inbox, "Failed to resolve record from notification")


def test_inbox_processing__fail__reviewer_not_found(db, rdm_record, superuser_identity, create_inbox):
    """Test inbox processing when the reviewer is not found."""
    recid = rdm_record.id

    notification_data = create_inbox_payload__review(recid)
    # Do not create reviewer, so actor_id won't match any reviewer

    inbox = create_inbox(
        recid=recid,
        raw=notification_data
    )

    assert_inbox_processing_failed(inbox, "Reviewer not found")


def test_inbox_processing__fail__not_a_member(
        db, rdm_record, superuser_identity,
        create_inbox,
        create_reviewer,
):
    """ Test inbox processing failure when user is not a member of the reviewer."""
    recid = rdm_record.id
    notification_data = create_inbox_payload__review(recid)

    reviewer = create_reviewer(actor_id=notification_data['actor']['id'])
    # Do not add superuser_identity as a member of the reviewer

    inbox = create_inbox(
        recid=recid,
        raw=notification_data
    )

    assert_inbox_processing_failed(inbox, "User is not a member of reviewer")
