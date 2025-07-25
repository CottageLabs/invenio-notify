from invenio_accounts.models import User
from invenio_notifications.models import Notification
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import UserEmailBackend
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records_resources.services import RecordEndpointLink
from invenio_users_resources.notifications.generators import EmailRecipient

from invenio_rdm_records.records.models import RDMRecordMetadata


def get_endorsement_noti_context(record=None, reviewer_name="Unknown", endorsement_url="Unknown", receiver_email="Unknown", user_id=None):
    """
    Build notification context with provided parameters.

    Args:
        record: The record object (optional)
        reviewer_name: Name of the reviewer (default: "Unknown")
        endorsement_url: URL of the endorsement (default: "Unknown")
        receiver_email: Email of the recipient (default: "Unknown")
        user_id: ID of the user who should receive the notification (optional)

    Returns:
        dict: Dictionary containing record_title, record_url, endorsement_url,
              reviewer_name, and receiver_email
    """

    record_title = "Unknown"
    record_url = "Unknown"

    # If receiver_email is "Unknown" and user_id is provided, try to get the email from the user
    if receiver_email == "Unknown" and user_id is not None:
        user = User.query.filter_by(id=user_id).first()
        if user:
            receiver_email = user.email

    if record:
        # Get record title
        try:
            record_title = record.data['metadata']['title']
        except Exception:
            pass

        # Get record URL
        try:
            r = RecordIdProviderV2.get(record.data['id'])
            rec_link = RecordEndpointLink("invenio_app_rdm_records.record_detail",
                                        params=["pid_value"],
                                        )
            record_url = rec_link.expand(r, {})
        except Exception:
            pass

    # Return data as dictionary
    return {
        'record_title': record_title,
        'record_url': record_url,
        'endorsement_url': endorsement_url,
        'reviewer_name': reviewer_name,
        'receiver_email': receiver_email,
    }


class NewEndorsementNotificationBuilder(NotificationBuilder):
    """Notification builder for record endorsement actions."""
    type = 'new-endorsement'

    @classmethod
    def build(cls, record: RDMRecordMetadata=None,
              reviewer_name="Unknown", endorsement_url="Unknown",
              receiver_email="Unknown", user_id=None):
        """
        Build notification with the provided parameters.

        Args:
            record: The record object (optional)
            reviewer_name: Name of the reviewer (default: "Unknown")
            endorsement_url: URL of the endorsement (default: "Unknown")
            receiver_email: Email of the recipient (default: "Unknown")
            user_id: ID of the user who should receive the notification (optional)

        Returns:
            Notification: A notification object with the context from the parameters
        """
        return Notification(
            type=cls.type,
            context=get_endorsement_noti_context(
                record=record,
                reviewer_name=reviewer_name,
                endorsement_url=endorsement_url,
                receiver_email=receiver_email,
                user_id=user_id
            ),
        )

    context = [
    ]

    recipients = [
        EmailRecipient("receiver_email"),
    ]

    recipient_filters = [
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]
