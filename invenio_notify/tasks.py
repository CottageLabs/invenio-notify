# TODO try to add CELERYBEAT_SCHEDULE, ref invenio_accounts/tasks.py, invenio_celery/__init__.py
import json
import logging
from celery import shared_task
from datetime import datetime
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError

from coarnotify.factory import COARNotifyFactory
from invenio_notify import constants
from invenio_notify.constants import REVIEW_TYPES
from invenio_notify.records.models import NotifyInboxModel
from invenio_notify.utils.notify_utils import get_record_id_by_record_url

log = logging.getLogger(__name__)


def mark_as_processed(inbox_record: db.Model, comment=None):
    """
    Mark an inbox record as processed by setting its process_date to today
    and optionally adding a comment.

    Args:
        inbox_record: The inbox record to mark as processed
        comment: Optional comment to add to the record
    """
    inbox_record.process_date = datetime.today()
    # TODO add comment field to NotifyInboxModel to store the error message
    # if comment is not None:
    #     inbox_record.comment = comment
    inbox_record.commit()


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

    # Extract reviewer ID from notification if available, otherwise use a default
    reviewer_id = notification_raw.get('actor', {}).get('id', 'unknown-reviewer')

    reviewer_type = 'unknown'
    for t in constants.REVIEW_TYPES:
        if t in notification_raw.get('type', []):
            reviewer_type = t
            break

    record_id = str(record_id)

    # Create the endorsement record data
    endorsement_data = {
        'metadata': {
            'record_id': record_id,
            'record_url': notification_raw['context']['id'],
            'result_url': notification_raw['object']['id'],
        },
        'record_id': record_id,
        'reviewer_id': reviewer_id,
        'review_type': reviewer_type,

        'user_id': user_id,
        'inbox_id': inbox_id,
    }

    # Create the endorsement record
    return endorsement_service.create(identity, endorsement_data)


def inbox_processing():
    # TODO handle review record
    # TODO should we send coar notification to the user if fail or rejected
    # TODO validate actor.id whether match with the user_id

    records_service = current_app.extensions["invenio-rdm-records"].records_service

    for inbox_record in NotifyInboxModel.search(None, [
        NotifyInboxModel.process_date.is_(None),
    ]):
        notification = COARNotifyFactory.get_by_object(json.loads(inbox_record.raw))
        notification_raw: dict = notification.to_jsonld()

        # Check if the notification type is supported
        if all(t not in REVIEW_TYPES for t in notification_raw.get('type', [])):
            # TODO how to handle if type is not in REVIEW_TYPES
            log.error(f'Unknown type: [{inbox_record.id=}]{notification_raw.get("type")}')
            mark_as_processed(inbox_record, "Notification type not supported")
            continue

        # Check if the notification context contains a record ID
        record_id = get_record_id_by_record_url(notification_raw['context']['id'])
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
        log.info(f"Created endorsement record: {endorsement.id}")

        # Mark inbox as processed after successful endorsement creation
        mark_as_processed(inbox_record, "Endorsement record created")


@shared_task
def shared_task_inbox_processing():
    inbox_processing()
