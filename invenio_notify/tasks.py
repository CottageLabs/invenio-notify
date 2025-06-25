import logging
from datetime import datetime

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db.uow import unit_of_work
from invenio_notifications.services.uow import NotificationOp
from invenio_pidstore.errors import PIDDoesNotExistError

from coarnotify.factory import COARNotifyFactory
from invenio_notify import constants
from invenio_notify.constants import SUPPORTED_TYPES
from invenio_notify.notifications.builders import NewEndorsementNotificationBuilder
from invenio_notify.records.models import NotifyInboxModel, ReviewerModel
from invenio_notify.utils.notify_utils import get_recid_by_record_url
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.models import RDMRecordMetadata

log = logging.getLogger(__name__)


@unit_of_work()
def mark_as_processed(inbox_record: NotifyInboxModel, comment=None, uow=None):
    """
    Mark an inbox record as processed by setting its process_date to today
    and optionally adding a comment.

    Args:
        inbox_record: The inbox record to mark as processed
        comment: Optional comment to add to the record
    """
    inbox_record.process_date = datetime.today()
    if comment is not None:
        inbox_record.process_note = comment


class ReviewerNotFoundError(Exception):
    """Custom exception for when a reviewer is not found."""
    pass


@unit_of_work()
def create_endorsement_record(identity, user_id, record_id, inbox_id, notification_raw,
                              uow=None):
    """
    Create a new endorsement record using the endorsement service.

    Args:
        identity: The identity to use for record creation
        record_id: The ID of the record being endorsed
        inbox_id: The ID of the notification inbox record
        notification_raw: The raw notification data

    Returns:
        The created endorsement record
    """
    endorsement_service = current_app.extensions["invenio-notify"].endorsement_service

    # Extract actor ID from notification
    actor_id = notification_raw.get('actor', {}).get('id', None)
    if not actor_id:
        log.warning(f"Could not extract actor_id from notification {inbox_id}")
        raise ReviewerNotFoundError(f"Actor ID not found in notification {inbox_id}")

    # Find ReviewerModel with matching actor_id
    reviewer = ReviewerModel.query.filter_by(actor_id=actor_id).first()
    if not reviewer:
        log.warning(f"Could not find reviewer with actor_id '{actor_id}'. Using None for reviewer_id.")
        raise ReviewerNotFoundError(f"Reviewer with actor_id '{actor_id}' not found")

    reviewer_id = reviewer.id
    log.info(f"Found reviewer ID {reviewer_id} for actor_id '{actor_id}'")

    reviewer_type = 'unknown'
    for t in constants.SUPPORTED_TYPES:
        if t in notification_raw.get('type', []):
            reviewer_type = t
            break

    record_id = str(record_id)

    review_url = notification_raw['object'].get(constants.KEY_INBOX_REVIEW_URL)
    if not review_url:
        log.warning(f"Could not extract review_url from notification {inbox_id} use object.id instead")

    # Create the endorsement record data
    endorsement_data = {
        'record_id': record_id,
        'reviewer_id': reviewer_id,
        'review_type': reviewer_type,
        'user_id': user_id,
        'inbox_id': inbox_id,
        'result_url': review_url,
        'reviewer_name': reviewer.name,
    }

    # Get reviewer name for notification
    reviewer_name = reviewer.name

    if reviewer_type == constants.TYPE_ENDORSEMENT:
        try:
            record = RDMRecordMetadata.query.filter_by(id=record_id).one()
        except Exception as e:
            log.warning(f"Could not resolve record for notification: {e}")
            record = None

        uow.register(
            NotificationOp(
                NewEndorsementNotificationBuilder.build(
                    record=record,
                    reviewer_name=reviewer_name,
                    endorsement_url=review_url,
                    user_id=user_id,   # KTODO user_id should user_id of record's owner instead of inbox sender
                ),
            )
        )

    # Create the endorsement record
    return endorsement_service.create(identity, endorsement_data, uow=uow)


def inbox_processing():
    tobe_update_records = []
    for inbox_record in NotifyInboxModel.search(None, [
        NotifyInboxModel.process_date.is_(None),
    ]):
        notification = COARNotifyFactory.get_by_object(inbox_record.raw)
        notification_raw: dict = notification.to_jsonld()

        # Check if the notification type is supported
        if all(t not in SUPPORTED_TYPES for t in notification_raw.get('type', [])):
            log.error(f'Unknown type: [{inbox_record.id=}]{notification_raw.get("type")}')
            mark_as_processed(inbox_record, "Notification type not supported")
            continue

        # Check if the notification context contains a record ID
        record_id = get_recid_by_record_url(notification_raw['context']['id'])
        if not record_id:
            log.error(f"Could not extract record_id from notification {inbox_record.id}")
            mark_as_processed(inbox_record, "Could not extract record_id from notification")
            continue

        log.info(f"Extracted record_id: {record_id} from notification {inbox_record.id}")

        # Get the record using the PID resolver
        try:
            # TODO study register_only=False, should we use registered_only=False
            record = current_rdm_records_service.record_cls.pid.resolve(record_id, registered_only=False)
            log.info(f"Successfully retrieved record with ID: {record_id}")

        except PIDDoesNotExistError:
            log.error(f"Record with ID {record_id} not found in the system")
            mark_as_processed(inbox_record, f"Record with ID {record_id} not found")
            continue

        # Create endorsement record
        try:
            endorsement = create_endorsement_record(
                system_identity,
                inbox_record.user_id,
                record.id,
                inbox_record.id,
                notification_raw
            )
        except ReviewerNotFoundError as e:
            log.warning(f"Failed to create endorsement record: {e}")
            mark_as_processed(inbox_record, comment="Reviewer not found")
            continue

        log.info(f"Created endorsement record: {endorsement._record.id}")

        # Mark inbox as processed after successful endorsement creation
        mark_as_processed(inbox_record)

        tobe_update_records.append(record)

    refresh_endorsements_field(tobe_update_records)


@unit_of_work()
def refresh_endorsements_field(records, uow=None):
    # re-commit rdm-record to refresh record.endorsements field
    existing_ids = set()
    for r in records:
        if r.id in existing_ids:
            continue
        r.commit()


@shared_task
def shared_task_inbox_processing():
    inbox_processing()
