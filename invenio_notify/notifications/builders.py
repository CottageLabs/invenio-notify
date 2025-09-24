import logging

from invenio_accounts.models import User
from invenio_notifications.models import Notification
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import UserEmailBackend
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records_resources.services import RecordEndpointLink
from invenio_users_resources.notifications.generators import EmailRecipient

from invenio_rdm_records.records.models import RDMRecordMetadata

from invenio_notify import constants

log = logging.getLogger(__name__)


def get_receiver_email(receiver_email, user_id):
    """
    Get receiver email, fallback to user lookup if email is None.
    
    Args:
        receiver_email: Email of the recipient
        user_id: ID of the user who should receive the notification (optional)
    
    Returns:
        str: The receiver email address
    """
    if receiver_email is None and user_id is not None:
        user = User.query.filter_by(id=user_id).first()
        if user:
            receiver_email = user.email
    return receiver_email or "Unknown"


def get_record_url(record):
    """
    Get record URL from record object.
    
    Args:
        record: The record object
    
    Returns:
        str: The record URL or "Unknown" if error occurs
    """
    try:
        r = RecordIdProviderV2.get(record.data['id'])
        rec_link = RecordEndpointLink("invenio_app_rdm_records.record_detail",
                                      params=["pid_value"],
                                      )
        return rec_link.expand(r, {})
    except Exception as e:
        log.warning(f"Error getting record URL: {e}")
        return "Unknown"


def get_record_title(record):
    """
    Get record title from record object.
    
    Args:
        record: The record object
    
    Returns:
        str: The record title or "Unknown" if error occurs
    """
    try:
        return record.data['metadata']['title']
    except Exception as e:
        log.warning(f"Error getting record title: {e}")
        return "Unknown"


class NewEndorsementNotificationBuilder(NotificationBuilder):
    """Notification builder for record endorsement actions."""
    type = 'new-endorsement'

    @classmethod
    def build(cls, record: RDMRecordMetadata = None,
              actor_name="Unknown", endorsement_url="Unknown",
              receiver_email=None, user_id=None):
        """
        Build notification with the provided parameters.

        Args:
            record: The record object (optional)
            actor_name: Name of the actor (default: "Unknown")
            endorsement_url: URL of the endorsement (default: "Unknown")
            receiver_email: Email of the recipient (default: "Unknown")
            user_id: ID of the user who should receive the notification (optional)

        Returns:
            Notification: A notification object with the context from the parameters
        """
        record_title = "Unknown"
        record_url = "Unknown"
        if record:
            record_title = get_record_title(record)
            record_url = get_record_url(record)

        context = {
            'record_title': record_title,
            'record_url': record_url,
            'endorsement_url': endorsement_url,
            'actor_name': actor_name,
            'receiver_email': get_receiver_email(receiver_email, user_id),
        }

        return Notification(type=cls.type, context=context, )

    context = []

    recipients = [
        EmailRecipient("receiver_email"),
    ]

    recipient_filters = []

    recipient_backends = [
        UserEmailBackend(),
    ]


class EndorsementUpdateNotificationBuilder(NotificationBuilder):
    """Notification builder for endorsement reply actions."""
    type = 'endorsement-update'

    @classmethod
    def build(cls, record: RDMRecordMetadata = None,
              actor_name="Unknown", endorsement_status="Unknown",
              receiver_email=None, user_id=None):
        """
        Build notification with the provided parameters.

        Args:
            record: The record object (optional)
            actor_name: Name of the actor (default: "Unknown")
            endorsement_status: Status of the endorsement (default: "Unknown")
            receiver_email: Email of the recipient (default: "Unknown")
            user_id: ID of the user who should receive the notification (optional)

        Returns:
            Notification: A notification object with the context from the parameters
        """
        record_title = "Unknown"
        record_url = "Unknown"
        if record:
            record_title = get_record_title(record)
            record_url = get_record_url(record)

        context = {
            'record_title': record_title,
            'record_url': record_url,
            'endorsement_status': endorsement_status,
            'actor_name': actor_name,
            'receiver_email': get_receiver_email(receiver_email, user_id),
            'WORKFLOW_STATUS_ANNOUNCE_REVIEW': constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW,
            'WORKFLOW_STATUS_REJECT': constants.WORKFLOW_STATUS_REJECT,
            'WORKFLOW_STATUS_TENTATIVE_ACCEPT': constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT,
            'WORKFLOW_STATUS_TENTATIVE_REJECT': constants.WORKFLOW_STATUS_TENTATIVE_REJECT,
        }

        return Notification(type=cls.type, context=context, )

    context = []

    recipients = [
        EmailRecipient("receiver_email"),
    ]

    recipient_filters = []

    recipient_backends = [
        UserEmailBackend(),
    ]
