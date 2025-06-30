import logging
from datetime import datetime
from typing import Optional, Union

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
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.models import RDMRecordMetadata, RDMParentMetadata

log = logging.getLogger(__name__)


def get_user_id_by_record(record) -> Optional[int]:
    """
    Get the user_id of the record owner by record object.
    
    Args:
        record: The RDMRecordMetadata object
        
    Returns:
        Optional[int]: The user_id of the record owner, or None if not found
    """
    if not record:
        log.warning("Record object is None")
        return None

    parent_id = record.parent_id

    # Get the parent record to find the owner
    parent = RDMParentMetadata.query.filter_by(id=parent_id).first()
    if not parent:
        log.warning(f"Parent record with id {parent_id} not found")
        return None

    # Extract user_id from parent JSON: access.owned_by.user
    access_data = parent.json.get('access', {})
    owned_by = access_data.get('owned_by', {})
    user_id = owned_by.get('user')

    if user_id is None:
        log.warning(f"Owner user_id not found in parent {parent_id} for record {record.id}")
        return None

    return int(user_id)


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


class DataNotFound(Exception):
    """Custom exception for when notification processing fails due to missing or invalid data."""
    pass


@unit_of_work()
def create_endorsement_record(identity, record_item: Union[str, RDMRecordMetadata], inbox_id, notification_raw,
                              uow=None):
    """
    Create a new endorsement record using the endorsement service.

    - email (sys notification) will be sent to the record owner
       if the endorsement type is 'endorsement' and saved successfully.

    Args:
        identity: The identity to use for record creation
        record_item: The record ID (string) or RDMRecordMetadata object
        inbox_id: The ID of the notification inbox record
        notification_raw: The raw notification data

    Returns:
        The created endorsement record
    """
    endorsement_service = current_app.extensions["invenio-notify"].endorsement_service

    # Extract actor ID from notification
    actor_id = notification_raw.get('actor', {}).get('id', None)
    if not actor_id:
        raise DataNotFound(f"Actor ID not found in notification {inbox_id}")

    # Find ReviewerModel with matching actor_id
    reviewer = ReviewerModel.query.filter_by(actor_id=actor_id).first()
    if not reviewer:
        raise DataNotFound(f"Reviewer with actor_id '{actor_id}' not found")

    reviewer_id = reviewer.id
    log.info(f"Found reviewer ID {reviewer_id} for actor_id '{actor_id}'")

    reviewer_type = 'unknown'
    for t in constants.SUPPORTED_TYPES:
        if t in notification_raw.get('type', []):
            reviewer_type = t
            break

    # Handle both string record_id and RDMRecordMetadata object
    if isinstance(record_item, str):
        record_id = record_item
        record = None  # Will be queried only if needed for endorsement type
    else:
        # record_item is RDMRecordMetadata object
        record = record_item
        record_id = str(record.id)

    review_url = notification_raw['object'].get(constants.KEY_INBOX_REVIEW_URL)
    if not review_url:
        log.warning(f"Could not extract review_url from notification {inbox_id} use object.id instead")

    # Create the endorsement record data
    endorsement_data = {
        'record_id': record_id,
        'reviewer_id': reviewer_id,
        'review_type': reviewer_type,
        'inbox_id': inbox_id,
        'result_url': review_url,
        'reviewer_name': reviewer.name,
    }

    # Get reviewer name for notification
    reviewer_name = reviewer.name

    if reviewer_type == constants.TYPE_ENDORSEMENT:
        # Get the record if we don't have it yet
        if record is None:
            record = RDMRecordMetadata.query.filter_by(id=record_id).first()
            if not record:
                raise DataNotFound(f"Record with ID {record_id} not found")

        record_owner_user_id = get_user_id_by_record(record)
        if record_owner_user_id is None:
            raise DataNotFound(f"User ID not found for record {record_id}")

        uow.register(
            NotificationOp(
                NewEndorsementNotificationBuilder.build(
                    record=record,
                    reviewer_name=reviewer_name,
                    endorsement_url=review_url,
                    user_id=record_owner_user_id,
                ),
            )
        )

    # Create the endorsement record
    return endorsement_service.create(identity, endorsement_data, uow=uow)


def resolve_record_from_notification(record_url: str) -> Optional[RDMRecord]:
    """
    Extract record ID from notification URL and resolve to RDMRecord.
    
    Args:
        record_url: The record URL from notification context
        
    Returns:
        RDMRecord if successfully resolved, None if extraction or resolution fails
    """
    # Extract record_id from URL
    record_id = get_recid_by_record_url(record_url)
    if not record_id:
        log.error(f"Could not extract record_id from notification")
        return None

    log.info(f"Extracted record_id: {record_id}")

    # Resolve record using PID
    try:
        # TODO study register_only=False, should we use registered_only=False
        record: RDMRecord = current_rdm_records_service.record_cls.pid.resolve(record_id, registered_only=False)
        log.info(f"Successfully retrieved record with ID: {record_id}")
        return record
    except PIDDoesNotExistError:
        log.error(f"Record with ID {record_id} not found in the system")
        return None


def process_endorsement_review(inbox_record: NotifyInboxModel, notification_raw: dict) -> bool:
    """
    Process endorsement review for a single inbox record.
    
    Args:
        inbox_record: The inbox record to process
        notification_raw: The raw notification data
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    # Resolve record from notification
    record_url = notification_raw['context']['id']
    record = resolve_record_from_notification(record_url)
    if record is None:
        mark_as_processed(inbox_record, "Failed to resolve record from notification")
        return False

    # Create endorsement record
    try:
        endorsement = create_endorsement_record(
            system_identity,
            record.model,
            inbox_record.id,
            notification_raw
        )
    except DataNotFound as e:
        log.warning(f"Failed to create endorsement record: {e}")
        mark_as_processed(inbox_record, comment="Reviewer not found")
        return False

    log.info(f"Created endorsement record: {endorsement._record.id}")

    # Mark inbox as processed after successful endorsement creation
    mark_as_processed(inbox_record)

    # re-commit rdm-record to refresh record.endorsements field
    record.commit()

    return True


def process_endorsement_reply(inbox_record: NotifyInboxModel, notification_raw: dict):
    raise NotImplementedError("Processing endorsement replies is not implemented yet.")


def inbox_processing():
    for inbox_record in NotifyInboxModel.unprocessed_records():
        try:
            notification = COARNotifyFactory.get_by_object(inbox_record.raw)
            notification_raw: dict = notification.to_jsonld()
        except Exception as e:
            msg = f"Failed to decode inbox json {inbox_record.id}: {e}"
            log.error(msg)
            mark_as_processed(inbox_record, msg)
            continue

        noti_type = notification_raw.get('type', [])

        # Check if the notification type is supported
        if all(t not in SUPPORTED_TYPES for t in noti_type):
            log.error(f'Unknown type: [{inbox_record.id=}]{notification_raw.get("type")}')
            mark_as_processed(inbox_record, "Notification type not supported")
            continue

        if any(t in {constants.TYPE_REVIEW, constants.TYPE_ENDORSEMENT} for t in noti_type):
            process_endorsement_review(inbox_record, notification_raw)
        else:
            process_endorsement_reply(inbox_record, notification_raw)


@shared_task
def shared_task_inbox_processing():
    inbox_processing()
