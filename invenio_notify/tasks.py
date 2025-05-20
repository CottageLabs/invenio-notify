import json
import logging
from datetime import datetime

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db.uow import unit_of_work
from invenio_pidstore.errors import PIDDoesNotExistError

from coarnotify.factory import COARNotifyFactory
from invenio_notify import constants
from invenio_notify.constants import REVIEW_TYPES
from invenio_notify.records.models import NotifyInboxModel, ReviewerModel
from invenio_notify.utils.notify_utils import get_recid_by_record_url

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


def create_endorsement_record(identity, user_id, record_id, inbox_id, notification_raw):
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

    # Extract actor ID (coar_id) from notification
    actor_id = notification_raw.get('actor', {}).get('id', 'unknown-reviewer')

    # Find ReviewerModel with matching coar_id
    reviewer = ReviewerModel.query.filter_by(coar_id=actor_id).first()
    if not reviewer:
        log.warning(f"Could not find reviewer with coar_id '{actor_id}'. Using None for reviewer_id.")
        raise ValueError(f"Reviewer with coar_id '{actor_id}' not found")

    reviewer_id = reviewer.id
    log.info(f"Found reviewer ID {reviewer_id} for coar_id '{actor_id}'")

    reviewer_type = 'unknown'
    for t in constants.REVIEW_TYPES:
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
    }

    # Create the endorsement record
    return endorsement_service.create(identity, endorsement_data)


def inbox_processing():

    records_service = current_app.extensions["invenio-rdm-records"].records_service

    for inbox_record in NotifyInboxModel.search(None, [
        NotifyInboxModel.process_date.is_(None),
    ]):
        notification = COARNotifyFactory.get_by_object(json.loads(inbox_record.raw))
        notification_raw: dict = notification.to_jsonld()

        # Check if the notification type is supported
        if all(t not in REVIEW_TYPES for t in notification_raw.get('type', [])):
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
            record = records_service.record_cls.pid.resolve(record_id, registered_only=False)
            log.info(f"Successfully retrieved record with ID: {record_id}")

        except PIDDoesNotExistError:
            log.error(f"Record with ID {record_id} not found in the system")
            mark_as_processed(inbox_record, f"Record with ID {record_id} not found")
            continue

        # Create endorsement record
        endorsement = create_endorsement_record(
            system_identity,
            inbox_record.user_id,
            record.id,
            inbox_record.id,
            notification_raw
        )
        log.info(f"Created endorsement record: {endorsement._record.id}")

        # Mark inbox as processed after successful endorsement creation
        mark_as_processed(inbox_record)


@shared_task
def shared_task_inbox_processing():
    inbox_processing()
