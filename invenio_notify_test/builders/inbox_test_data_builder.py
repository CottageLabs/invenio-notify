import pytest

from invenio_notify.utils import actor_utils


@pytest.fixture
def inbox_test_data_builder(
    db,
    create_actor,
    create_endorsement_request,
    create_inbox,
    rdm_record,
    superuser_identity,
):
    class _InboxTestDataBuilder:
        """Builder class for creating inbox test data with a fluent interface."""

        def __init__(self, record_id, notification_data, user_identity=None):
            """Initialize the builder with core dependencies and fixtures.

            Args:
                record_id: RDM record ID
                user_identity: User identity object (defaults to superuser_identity if None)
                notification_data: Notification data dictionary
            """
            self.record_id = record_id
            self.user_identity = user_identity if user_identity is not None else superuser_identity
            self.notification_data = notification_data
            self.db = db
            self._create_actor_fixture = create_actor
            self._create_endorsement_request_fixture = create_endorsement_request
            self._create_inbox_fixture = create_inbox

            # Store created objects for later access
            self.actor = None
            self.endorsement_request = None
            self.inbox = None

        def create_actor(self):
            """Create a actor with actor_id from notification_data."""
            # Create actor with actor_id from notification data
            actor_id = self.notification_data['actor']['id']
            self.actor = self._create_actor_fixture(actor_id=actor_id)
            return self

        def add_member_to_actor(self):
            """Add superuser as a member to the actor."""
            if self.actor is None:
                raise ValueError("Actor must be created first")

            actor_utils.add_member_to_actor(self.actor.id, self.user_identity.id)
            return self

        def create_endorsement_request(self, notification_id=None):
            """Create an endorsement request with notification_id from notification_data."""
            if self.actor is None:
                raise ValueError("Actor must be created first")

            from invenio_rdm_records.proxies import current_rdm_records

            # Resolve record to get its UUID
            record = current_rdm_records.records_service.record_cls.pid.resolve(self.record_id)

            # Create endorsement request with notification_id from inReplyTo
            self.endorsement_request = self._create_endorsement_request_fixture(
                record_id=record.id,
                actor_id=self.actor.id,
                user_id=self.user_identity.id,
                notification_id=notification_id or self.notification_data['inReplyTo']
            )
            return self

        def create_inbox(self):
            """Create an inbox with the notification data."""
            # Create inbox record with notification data
            self.inbox = self._create_inbox_fixture(
                record_id=self.record_id,
                raw=self.notification_data
            )
            return self

    return _InboxTestDataBuilder