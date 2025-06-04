from invenio_accounts.models import User
from invenio_notifications.models import Notification
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import UserEmailBackend
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records_resources.services import RecordEndpointLink
from invenio_users_resources.notifications.generators import EmailRecipient

from invenio_notify.records.models import EndorsementModel


def get_endorsement_noti_context(endorsement):
    """
    Extract data from an endorsement and return it as a dictionary.

    Args:
        endorsement: The EndorsementModel instance

    Returns:
        dict: Dictionary containing record_name, record_url, endorsement_url,
              reviewer_name, and receiver_email
    """

    record_title = "Unknown"
    record_url = "Unknown"

    if endorsement.record:
        # Get record title
        try:
            record_title = endorsement.record.data['metadata']['title']
        except Exception:
            pass

        # Get record URL
        r = RecordIdProviderV2.get(endorsement.record.data['id'])
        rec_link = RecordEndpointLink("invenio_app_rdm_records.record_detail",
                                      params=["pid_value"],
                                      )
        record_url = rec_link.expand(r, {})
    else:
        print(f"Endorsement {endorsement.id} has no associated record.")


    # Get reviewer information
    reviewer_name = "Unknown"
    if endorsement.reviewer:
        reviewer_name = endorsement.reviewer.name

    # Get user email
    receiver_email = "Unknown"
    if endorsement.user_id:
        user = User.query.filter_by(id=endorsement.user_id).first()
        if user:
            receiver_email = user.email

    # Build endorsement URL
    endorsement_url = endorsement.result_url if endorsement.result_url else f"https://example.com/endorsement/{endorsement.id}"

    # Return data as dictionary
    return {
        'record_title': record_title,
        'record_url': record_url,
        'endorsement_url': endorsement_url,
        'reviewer_name': reviewer_name,
        'receiver_email': receiver_email,
    }



class TmpNotificationBuilder(NotificationBuilder):
    """Notification builder for inclusion actions."""
    type = 'tmp-noti'

    @classmethod
    def build(cls, endorsement: 'EndorsementModel'):
        """Build notification with request context."""
        # raise NotImplementedError()
        return Notification(
            type=cls.type,
            context={
                # "request": EntityResolverRegistry.reference_entity(request),
                # "executing_user": EntityResolverRegistry.reference_identity(identity),
                **get_endorsement_noti_context(endorsement),
                # 'data': {
                #     # KTODO dump request data here for now
                #     'record_name': 'Test Record Name',
                #     'record_url': 'https://example.com/record/12345',
                #     'endorsement_url': 'https://example.com/endorsement/67890',
                #     'reviewer_name': 'Reviewer Name',
                #     'receiver_email': 'kkh900922@gmail.com',
                # },
            },
        )

    context = [
        # EntityResolve(key="data.title"),
    ]

    recipients = [
        EmailRecipient("receiver_email"),
    ]

    recipient_filters = [
        # UserPreferencesRecipientFilter(),
        # UserRecipientFilter("executing_user"),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]
