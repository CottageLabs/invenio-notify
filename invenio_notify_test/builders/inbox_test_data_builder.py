import pytest

from invenio_notify.utils import reviewer_utils


@pytest.fixture
def inbox_test_data_builder(
    db,
    create_reviewer,
    create_endorsement_request,
    create_inbox,
    rdm_record,
    superuser_identity,
):
    class _InboxTestDataBuilder:
        """Builder class for creating inbox test data with a fluent interface."""

        def __init__(self, rdm_record_item, notification_data, user_identity=None):
            """Initialize the builder with core dependencies and fixtures.

            Args:
                rdm_record_item: RDM record object
                user_identity: User identity object (defaults to superuser_identity if None)
                notification_data: Notification data dictionary
            """
            self.rdm_record = rdm_record_item
            self.user_identity = user_identity if user_identity is not None else superuser_identity
            self.notification_data = notification_data
            self.db = db
            self._create_reviewer_fixture = create_reviewer
            self._create_endorsement_request_fixture = create_endorsement_request
            self._create_inbox_fixture = create_inbox

            # Store created objects for later access
            self.reviewer = None
            self.endorsement_request = None
            self.inbox = None

        def create_reviewer(self):
            """Create a reviewer with actor_id from notification_data."""
            # Create reviewer with actor_id from notification data
            actor_id = self.notification_data['actor']['id']
            self.reviewer = self._create_reviewer_fixture(actor_id=actor_id)
            return self

        def add_member_to_reviewer(self):
            """Add superuser as a member to the reviewer."""
            if self.reviewer is None:
                raise ValueError("Reviewer must be created first")

            reviewer_utils.add_member_to_reviewer(self.reviewer.id, self.user_identity.id)
            return self

        def create_endorsement_request(self, noti_id=None):
            """Create an endorsement request with noti_id from notification_data."""
            if self.reviewer is None:
                raise ValueError("Reviewer must be created first")

            from invenio_rdm_records.proxies import current_rdm_records

            # Resolve record to get its UUID
            record = current_rdm_records.records_service.record_cls.pid.resolve(self.rdm_record.id)

            # Create endorsement request with noti_id from inReplyTo
            self.endorsement_request = self._create_endorsement_request_fixture(
                record_id=record.id,
                reviewer_id=self.reviewer.id,
                user_id=self.user_identity.id,
                noti_id=noti_id or self.notification_data['inReplyTo']
            )
            return self

        def create_inbox(self):
            """Create an inbox with the notification data."""
            # Create inbox record with notification data
            self.inbox = self._create_inbox_fixture(
                recid=self.rdm_record.id,
                raw=self.notification_data
            )
            return self

    return _InboxTestDataBuilder