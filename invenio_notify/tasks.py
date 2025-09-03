import logging
from datetime import datetime, timezone
from typing import Optional, Union

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db.uow import unit_of_work
from invenio_notifications.services.uow import NotificationOp
from invenio_pidstore.errors import PIDDoesNotExistError

from coarnotify.factory import COARNotifyFactory
from invenio_db import db
from invenio_notify import constants
from invenio_notify.constants import SUPPORTED_TYPES
from invenio_notify.notifications.builders import NewEndorsementNotificationBuilder, \
    EndorsementUpdateNotificationBuilder
from invenio_notify.records.models import EndorsementReplyModel, EndorsementRequestModel
from invenio_notify.records.models import NotifyInboxModel, ReviewerModel
from invenio_notify.utils.notify_utils import get_recid_by_record_url
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.models import RDMRecordMetadata, RDMParentMetadata

log = logging.getLogger(__name__)


def get_record_by_id(record_id) -> RDMRecordMetadata:
    """
    Get RDMRecordMetadata by record ID.

    Args:
        record_id: The record uuid

    Returns:
        RDMRecordMetadata: The record metadata object

    Raises:
        DataNotFound: If record is not found
    """
    record = RDMRecordMetadata.query.filter_by(id=record_id).first()
    if not record:
        raise DataNotFound(f"Record with ID {record_id} not found")
    return record


def create_endorsement_update_notification(record_id: str, reviewer_name: str,
                                           noti_type: str, uow) -> None:
    record = get_record_by_id(record_id)
    record_owner_user_id = get_user_id_by_record(record)
    uow.register(
        NotificationOp(
            EndorsementUpdateNotificationBuilder.build(
                record=record,
                reviewer_name=reviewer_name,
                user_id=record_owner_user_id,
                endorsement_status=noti_type,
            ),
        )
    )


def get_user_id_by_record(record: RDMRecordMetadata) -> int:
    """
    Get the user_id of the record owner by record object.
    
    Args:
        record: The RDMRecordMetadata object
        
    Returns:
        int: The user_id of the record owner

    Raises:
        DataNotFound: If record is None, parent not found, or user_id not found
    """
    if not record:
        log.warning("Record object is None")
        raise DataNotFound("User ID not found for record")

    parent_id = record.parent_id

    # Get the parent record to find the owner
    parent = RDMParentMetadata.query.filter_by(id=parent_id).first()
    if not parent:
        log.warning(f"Parent record with id {parent_id} not found")
        raise DataNotFound("User ID not found for record")

    # Extract user_id from parent JSON: access.owned_by.user
    access_data = parent.json.get('access', {})
    owned_by = access_data.get('owned_by', {})
    user_id = owned_by.get('user')

    if user_id is None:
        log.warning(f"Owner user_id not found in parent {parent_id} for record {record.id}")
        raise DataNotFound("User ID not found for record")

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
    inbox_record.process_date = datetime.now(timezone.utc)
    if comment is not None:
        inbox_record.process_note = comment


class DataNotFound(Exception):
    """Custom exception for when notification processing fails due to missing or invalid data."""

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)
        self.message = message


def get_notification_type(notification_raw: dict) -> str | None:
    """
    Extract notification type from raw notification data.
    
    Args:
        notification_raw: The raw notification data
        
    Returns:
        str | None: The first supported type found, or None if no supported type exists
    """
    noti_types = notification_raw.get('type', [])
    if isinstance(noti_types, str):
        noti_types = [noti_types]

    for t in SUPPORTED_TYPES:
        if t in noti_types:
            return t
    return None


def get_reviewer_by_actor_id(notification_raw: dict) -> ReviewerModel:
    """
    Extract reviewer data from notification by actor ID.
    
    Args:
        notification_raw: The raw notification data
        
    Returns:
        ReviewerModel if found
        
    Raises:
        DataNotFound: If actor ID is not found or reviewer doesn't exist
    """
    # Extract actor ID from notification
    actor_id = notification_raw.get('actor', {}).get('id', None)
    if not actor_id:
        raise DataNotFound(f"Actor ID not found in notification, actor[{actor_id}]")

    # Find ReviewerModel with matching actor_id
    reviewer = ReviewerModel.query.filter_by(actor_id=actor_id).first()
    if not reviewer:
        raise DataNotFound(f"Reviewer not found, actor_id[{actor_id}]")

    return reviewer


@unit_of_work()
def create_endorsement_record(identity, record_item: Union[str, RDMRecordMetadata], inbox_id, notification_raw,
                              reviewer: ReviewerModel, endo_reply_id: Optional[int] = None, uow=None):
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

    reviewer_id = reviewer.id
    log.info(f"Found reviewer ID {reviewer_id} for actor_id '{reviewer.actor_id}'")

    reviewer_type = get_notification_type(notification_raw)
    if not reviewer_type:
        raise DataNotFound(f"Notification type not found in notification {inbox_id}")

    # Handle both string record_id and RDMRecordMetadata object
    if isinstance(record_item, str):
        record = None  # Will be queried only if needed for endorsement type
        record_id = record_item
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
        'endorsement_reply_id': endo_reply_id,
    }

    # Get reviewer name for notification
    reviewer_name = reviewer.name

    if reviewer_type == constants.TYPE_ENDORSEMENT:
        # Get the record if we don't have it yet
        record = record or get_record_by_id(record_id)
        uow.register(
            NotificationOp(
                NewEndorsementNotificationBuilder.build(
                    record=record,
                    reviewer_name=reviewer_name,
                    endorsement_url=review_url,
                    user_id=get_user_id_by_record(record),
                ),
            )
        )
    elif reviewer_type == constants.TYPE_REVIEW:
        create_endorsement_update_notification(
            record_id,
            reviewer_name,
            reviewer_type,
            uow
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


@unit_of_work()
def handle_endorsement_and_review(inbox_record: NotifyInboxModel,
                                  notification_raw: dict,
                                  reviewer: ReviewerModel,
                                  endo_reply_id: Optional[int] = None,
                                  uow=None, ):
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
        raise DataNotFound(f"Failed to resolve record from notification")

    # Create endorsement record
    endorsement = create_endorsement_record(
        system_identity,
        record.model,
        inbox_record.id,
        notification_raw,
        reviewer,
        endo_reply_id
    )

    log.info(f"Created endorsement record: {endorsement._record.id}")

    record_ids = [row[0] for row in db.session.query(RDMRecordMetadata.id).filter_by(parent_id=record.parent.id).all()]

    # Iterate over all RDMRecordMetadata records with this parent_id
    for record_id in record_ids:
        # Indexing the record will add the endorsement data via EndorsementsDumperExt
        current_rdm_records_service.indexer.index_by_id(record_id)


@unit_of_work()
def handle_endorsement_reply(inbox_record: NotifyInboxModel,
                             notification_raw: dict, uow=None) -> Optional[EndorsementReplyModel]:
    """
    Process endorsement reply for a single inbox record.
    Creates a new EndorsementReplyModel record.
    
    Args:
        inbox_record: The inbox record to process
        notification_raw: The raw notification data
        
    Returns:
        bool: True if processing was successful, False otherwise
    """

    # Extract noti_id from inReplyTo field
    noti_id = notification_raw.get('inReplyTo', '')
    if not noti_id:
        log.debug(f"Notification {inbox_record.id} does not have inReplyTo field")
        return

    # Find the endorsement request using noti_id instead of reviewer_id
    endorsement_request = EndorsementRequestModel.query.filter_by(noti_id=noti_id).first()
    if not endorsement_request:
        log.debug(f"Endorsement request with noti_id {noti_id} not found")
        raise DataNotFound(f"Endorsement request not found for notification id[{inbox_record.id}], noti_id[{noti_id}]")

    # Extract status from notification type
    noti_type = get_notification_type(notification_raw)
    if not noti_type:
        raise DataNotFound(f"Notification type not found in notification {inbox_record.id}")
    # Extract message from notification if available
    message = notification_raw.get('object', {}).get('summary', None)

    # Create the endorsement reply record
    if noti_type not in {constants.TYPE_REVIEW, constants.TYPE_ENDORSEMENT}:
        # Review's notification will be sent when endorsement record is created
        create_endorsement_update_notification(
            endorsement_request.record_id,
            endorsement_request.reviewer.name,
            noti_type,
            uow
        )

    reply = EndorsementReplyModel.create({
        'endorsement_request_id': endorsement_request.id,
        'inbox_id': inbox_record.id,
        'status': noti_type,
        'message': message
    })
    log.info(f"Created endorsement reply record: {reply.id}")

    # Update endorsement_request.latest_status
    endorsement_request.latest_status = noti_type

    return reply


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

        noti_type = get_notification_type(notification_raw)

        # Check if the notification type is supported
        if not noti_type:
            log.error(f'Unknown type: [{inbox_record.id=}]{notification_raw.get("type")}')
            mark_as_processed(inbox_record, "Notification type not supported")
            continue

        # Get reviewer using the utility function
        try:
            reviewer = get_reviewer_by_actor_id(notification_raw)
        except DataNotFound as e:
            log.warning(f"Failed to get reviewer: {e}")
            mark_as_processed(inbox_record, e.message)
            continue

        # Check if noti sender is a member of the reviewer
        if not ReviewerModel.has_member(inbox_record.user_id, reviewer.actor_id):
            log.warning(f"User {inbox_record.user_id} is not a member of reviewer {reviewer.actor_id}")
            mark_as_processed(inbox_record, "User is not a member of reviewer")
            continue

        try:
            reply = handle_endorsement_reply(inbox_record, notification_raw)
            if noti_type in {constants.TYPE_REVIEW, constants.TYPE_ENDORSEMENT}:
                endo_reply_id = reply.id if reply else None
                handle_endorsement_and_review(inbox_record, notification_raw, reviewer, endo_reply_id)

            # Mark inbox as processed after successful reply creation
            mark_as_processed(inbox_record)
        except DataNotFound as e:
            log.warning(f"Failed to process inbox record {inbox_record.id}: {e}")
            mark_as_processed(inbox_record, e.message)


@shared_task
def shared_task_inbox_processing():
    inbox_processing()
