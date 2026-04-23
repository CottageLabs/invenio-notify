#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.
import logging
from typing import Optional, Union

from coarnotify.core.notify import NotifyPattern
from flask import current_app

from invenio_db.uow import unit_of_work
from invenio_db import db
from invenio_notifications.services.uow import NotificationOp

from invenio_notify.notifications.builders import EndorsementUpdateNotificationBuilder, \
    NewEndorsementNotificationBuilder
from invenio_rdm_records.proxies import current_rdm_records_service

from invenio_rdm_records.records.models import RDMRecordMetadata
from marshmallow import ValidationError

from invenio_notify import constants
from invenio_notify.constants import TYPE_REVIEW, TYPE_ENDORSEMENT, TYPE_TENTATIVE_ACCEPT, TYPE_REJECT, \
    TYPE_TENTATIVE_REJECT
from invenio_notify.records.models import NotifyInboxModel, EndorsementReplyModel, EndorsementRequestModel, ActorModel
from invenio_notify.workflows.core import mark_as_processed, DataNotFound, resolve_record_from_notification, \
    get_record_by_id, get_user_id_by_record, identify_supported_type

from invenio_access.permissions import system_identity

log = logging.getLogger(__name__)

SUPPORTED_TYPES = [TYPE_REVIEW, TYPE_ENDORSEMENT, TYPE_TENTATIVE_ACCEPT, TYPE_REJECT, TYPE_TENTATIVE_REJECT]

def process_next_notification(inbox_record, notification, actor):

    # notification_raw: dict = notification.to_jsonld()
    noti_type = identify_supported_type(notification, supported=SUPPORTED_TYPES)

    # Check if the notification type is supported
    if not noti_type:
        log.error(f'Unknown type: [{inbox_record.id=}]{notification.type}')
        #mark_as_processed(inbox_record, "Notification type not supported")
        return

    try:
        reply = handle_endorsement_reply(inbox_record, notification)
        if noti_type in {constants.TYPE_REVIEW, constants.TYPE_ENDORSEMENT}:
            endo_reply_id = reply.id if reply else None
            handle_endorsement_and_review(inbox_record, notification, actor, endo_reply_id)

        # Mark inbox as processed after successful reply creation
        mark_as_processed(inbox_record)
    except DataNotFound as e:
        log.warning(f"Failed to process inbox record {inbox_record.id}: {e}")
        mark_as_processed(inbox_record, e.message)
    except ValidationError as e:
        log.warning(f"Failed to process inbox record {inbox_record.id}, validation error: {e}")
        mark_as_processed(inbox_record, str(e))


# @unit_of_work()
# def handle_endorsement_reply(inbox_record: NotifyInboxModel,
#                              notification_raw: dict, uow=None) -> Optional[EndorsementReplyModel]:
#     """
#     Process endorsement reply for a single inbox record.
#     Creates a new EndorsementReplyModel record.
#
#     Args:
#         inbox_record: The inbox record to process
#         notification_raw: The raw notification data
#
#     Returns:
#         bool: True if processing was successful, False otherwise
#     """
#
#     # Extract notification_id from inReplyTo field
#     notification_id = notification_raw.get('inReplyTo', '')
#     if not notification_id:
#         log.debug(f"Notification {inbox_record.id} does not have inReplyTo field")
#         return
#
#     # Find the endorsement request using notification_id instead of actor_id
#     endorsement_request = EndorsementRequestModel.query.filter_by(notification_id=notification_id).first()
#     if not endorsement_request:
#         log.debug(f"Endorsement request with notification_id {notification_id} not found")
#         raise DataNotFound(
#             f"Endorsement request not found for notification id[{inbox_record.id}], notification_id[{notification_id}]")
#
#     # Extract workflow status from notification
#     workflow_status = get_workflow_status(notification_raw)
#     if not workflow_status:
#         raise DataNotFound(f"Notification type not found in notification {inbox_record.id}")
#     # Extract message from notification if available
#     message = notification_raw.get('object', {}).get('summary', None)
#
#     # Create the endorsement reply record
#     if workflow_status not in {constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT,
#                                constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW}:
#         # Review's notification will be sent when endorsement record is created
#         create_endorsement_update_notification(
#             endorsement_request.record_id,
#             endorsement_request.actor.name,
#             workflow_status,
#             uow
#         )
#
#     reply = EndorsementReplyModel.create({
#         'endorsement_request_id': endorsement_request.id,
#         'inbox_id': inbox_record.id,
#         'status': workflow_status,
#         'message': message
#     })
#     log.info(f"Created endorsement reply record: {reply.id}")
#
#     # Update endorsement_request.latest_status with workflow status
#     endorsement_request.latest_status = workflow_status
#
#     return reply

@unit_of_work()
def handle_endorsement_reply(inbox_record: NotifyInboxModel,
                             notification: NotifyPattern, uow=None) -> Optional[EndorsementReplyModel]:
    """
    Process endorsement reply for a single inbox record.
    Creates a new EndorsementReplyModel record.

    Args:
        inbox_record: The inbox record to process
        notification_raw: The raw notification data

    Returns:
        bool: True if processing was successful, False otherwise
    """

    # Extract notification_id from inReplyTo field
    notification_id = notification.in_reply_to
    if not notification_id:
        log.debug(f"Notification {inbox_record.id} does not have inReplyTo field")
        return

    # Find the endorsement request using notification_id instead of actor_id
    endorsement_request = EndorsementRequestModel.query.filter_by(notification_id=notification_id).first()
    if not endorsement_request:
        log.debug(f"Endorsement request with notification_id {notification_id} not found")
        raise DataNotFound(
            f"Endorsement request not found for notification id[{inbox_record.id}], notification_id[{notification_id}]")

    # Extract workflow status from notification
    workflow_status = get_workflow_status(notification)
    if not workflow_status:
        raise DataNotFound(f"Notification type not found in notification {inbox_record.id}")

    # Extract message from notification if available
    message = None
    if hasattr(notification, 'summary'):
        message = notification.summary

    # Create the endorsement reply record
    if workflow_status not in {constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT,
                               constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW}:
        # Review's notification will be sent when endorsement record is created
        create_endorsement_update_notification(
            endorsement_request.record_id,
            endorsement_request.actor.name,
            workflow_status,
            uow
        )

    reply = EndorsementReplyModel.create({
        'endorsement_request_id': endorsement_request.id,
        'inbox_id': inbox_record.id,
        'status': workflow_status,
        'message': message
    })
    log.info(f"Created endorsement reply record: {reply.id}")

    # Update endorsement_request.latest_status with workflow status
    endorsement_request.latest_status = workflow_status

    return reply


# @unit_of_work()
# def handle_endorsement_and_review(inbox_record: NotifyInboxModel,
#                                   notification_raw: dict,
#                                   actor: ActorModel,
#                                   endo_reply_id: Optional[int] = None,
#                                   uow=None, ):
#     """
#     Process endorsement review for a single inbox record.
#
#     Args:
#         inbox_record: The inbox record to process
#         notification_raw: The raw notification data
#         actor: The actor associated with the notification
#         endo_reply_id: Id of the endorsement reply if applicable
#
#     Returns:
#         bool: True if processing was successful, False otherwise
#     """
#     # Resolve record from notification
#     record_url = notification_raw['context']['id']
#     record = resolve_record_from_notification(record_url)
#     if record is None:
#         raise DataNotFound(f"Failed to resolve record from notification")
#
#     # Create endorsement record
#     endorsement = create_endorsement_record(
#         system_identity,
#         record.model,
#         inbox_record.id,
#         notification_raw,
#         actor,
#         endo_reply_id
#     )
#
#     log.info(f"Created endorsement record: {endorsement._record.id}")
#
#     record_ids = [row[0] for row in db.session.query(RDMRecordMetadata.id).filter_by(parent_id=record.parent.id).all()]
#
#     # Iterate over all RDMRecordMetadata records with this parent_id
#     for record_id in record_ids:
#         # Indexing the record will add the endorsement data via EndorsementsDumperExt
#         current_rdm_records_service.indexer.index_by_id(record_id)

@unit_of_work()
def handle_endorsement_and_review(inbox_record: NotifyInboxModel,
                                  notification: NotifyPattern,
                                  actor: ActorModel,
                                  endo_reply_id: Optional[int] = None,
                                  uow=None, ):
    """
    Process endorsement review for a single inbox record.

    Args:
        inbox_record: The inbox record to process
        notification_raw: The raw notification data
        actor: The actor associated with the notification
        endo_reply_id: Id of the endorsement reply if applicable

    Returns:
        bool: True if processing was successful, False otherwise
    """
    # Resolve record from notification
    record_url = None
    if notification.context:
        record_url = notification.context.id

    record = resolve_record_from_notification(record_url)
    if record is None:
        raise DataNotFound(f"Failed to resolve record from notification")

    # Create endorsement record
    endorsement = create_endorsement_record(
        system_identity,
        record.model,
        inbox_record.id,
        notification,
        actor,
        endo_reply_id
    )

    log.info(f"Created endorsement record: {endorsement._record.id}")

    record_ids = [row[0] for row in db.session.query(RDMRecordMetadata.id).filter_by(parent_id=record.parent.id).all()]

    # Iterate over all RDMRecordMetadata records with this parent_id
    for record_id in record_ids:
        # Indexing the record will add the endorsement data via EndorsementsDumperExt
        current_rdm_records_service.indexer.index_by_id(record_id)

# def get_workflow_status(notification_raw: dict) -> str | None:
#     """
#     Extract workflow status from notification type field based on COAR notification structure.
#
#     Args:
#         notification_raw: The raw notification data
#
#     Returns:
#         str | None: The workflow status constant
#     """
#
#     # Extract type field from notification
#     type_field = notification_raw.get('type', [])
#
#     # If type field is empty or missing, return None
#     if not type_field:
#         return None
#
#     # Ensure type_field is a list for consistent processing
#     if isinstance(type_field, str):
#         type_field = [type_field]
#
#     # Check for simple single-type notifications first
#     for t in type_field:
#         if t == constants.TYPE_TENTATIVE_ACCEPT:
#             return constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT
#         elif t == constants.TYPE_TENTATIVE_REJECT:
#             return constants.WORKFLOW_STATUS_TENTATIVE_REJECT
#         elif t == constants.TYPE_REJECT:
#             return constants.WORKFLOW_STATUS_REJECT
#
#     # Check for compound types with activities
#     has_announce = 'Announce' in type_field
#
#     # Map based on activity + notification type combinations
#     if has_announce and constants.TYPE_ENDORSEMENT in type_field:
#         return constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT
#     elif has_announce and constants.TYPE_REVIEW in type_field:
#         return constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW
#
#     return None

def get_workflow_status(notification: NotifyPattern) -> str | None:
    """
    Extract workflow status from notification type field based on COAR notification structure.

    Args:
        notification_raw: The raw notification data

    Returns:
        str | None: The workflow status constant
    """

    # Extract type field from notification
    type_field = notification.type

    # If type field is empty or missing, return None
    if not type_field:
        return None

    # Ensure type_field is a list for consistent processing
    if isinstance(type_field, str):
        type_field = [type_field]

    # Check for simple single-type notifications first
    for t in type_field:
        if t == constants.TYPE_TENTATIVE_ACCEPT:
            return constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT
        elif t == constants.TYPE_TENTATIVE_REJECT:
            return constants.WORKFLOW_STATUS_TENTATIVE_REJECT
        elif t == constants.TYPE_REJECT:
            return constants.WORKFLOW_STATUS_REJECT

    # Check for compound types with activities
    has_announce = 'Announce' in type_field

    # Map based on activity + notification type combinations
    if has_announce and constants.TYPE_ENDORSEMENT in type_field:
        return constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT
    elif has_announce and constants.TYPE_REVIEW in type_field:
        return constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW

    return None

def create_endorsement_update_notification(record_id: str, actor_name: str,
                                           noti_type: str, uow) -> None:
    record = get_record_by_id(record_id)
    record_owner_user_id = get_user_id_by_record(record)
    uow.register(
        NotificationOp(
            EndorsementUpdateNotificationBuilder.build(
                record=record,
                actor_name=actor_name,
                user_id=record_owner_user_id,
                endorsement_status=noti_type,
            ),
        )
    )

# @unit_of_work()
# def create_endorsement_record(identity, record_item: Union[str, RDMRecordMetadata], inbox_id, notification_raw,
#                               actor: ActorModel, endo_reply_id: Optional[int] = None, uow=None):
#     """
#     Create a new endorsement record using the endorsement service.
#
#     - email (sys notification) will be sent to the record owner
#        if the endorsement type is 'endorsement' and saved successfully.
#
#     Args:
#         identity: The identity to use for record creation
#         record_item: The record ID (string) or RDMRecordMetadata object
#         inbox_id: The ID of the notification inbox record
#         notification_raw: The raw notification data
#         actor: The actor associated with the notification
#         endo_reply_id: Id of the endorsement reply if applicable
#
#     Returns:
#         The created endorsement record
#     """
#     endorsement_service = current_app.extensions["invenio-notify"].endorsement_service
#
#     actor_id = actor.id
#     log.info(f"Found actor ID {actor_id} for actor_id '{actor.actor_id}'")
#
#     noti_type = identify_supported_type(notification_raw)
#     if not noti_type:
#         raise DataNotFound(f"Notification type not found in notification {inbox_id}")
#
#     # Handle both string record_id and RDMRecordMetadata object
#     if isinstance(record_item, str):
#         record = None  # Will be queried only if needed for endorsement type
#         record_id = record_item
#     else:
#         # record_item is RDMRecordMetadata object
#         record = record_item
#         record_id = str(record.id)
#
#     review_url = notification_raw['object'].get(constants.KEY_INBOX_REVIEW_URL) or notification_raw['object'].get('id')
#
#     # Create the endorsement record data
#     endorsement_data = {
#         'record_id': record_id,
#         'actor_id': actor_id,
#         'review_type': noti_type,
#         'inbox_id': inbox_id,
#         'result_url': review_url,
#         'actor_name': actor.name,
#         'endorsement_reply_id': endo_reply_id,
#     }
#
#     # Get actor name for notification
#     actor_name = actor.name
#
#     if noti_type == constants.TYPE_ENDORSEMENT:
#         # Get the record if we don't have it yet
#         record = record or get_record_by_id(record_id)
#         uow.register(
#             NotificationOp(
#                 NewEndorsementNotificationBuilder.build(
#                     record=record,
#                     actor_name=actor_name,
#                     endorsement_url=review_url,
#                     user_id=get_user_id_by_record(record),
#                 ),
#             )
#         )
#     elif noti_type == constants.TYPE_REVIEW:
#         create_endorsement_update_notification(
#             record_id,
#             actor_name,
#             constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW,
#             uow
#         )
#
#
#     # Create the endorsement record
#     return endorsement_service.create(identity, endorsement_data, uow=uow)

@unit_of_work()
def create_endorsement_record(identity, record_item: Union[str, RDMRecordMetadata], inbox_id, notification: NotifyPattern,
                              actor: ActorModel, endo_reply_id: Optional[int] = None, uow=None):
    """
    Create a new endorsement record using the endorsement service.

    - email (sys notification) will be sent to the record owner
       if the endorsement type is 'endorsement' and saved successfully.

    Args:
        identity: The identity to use for record creation
        record_item: The record ID (string) or RDMRecordMetadata object
        inbox_id: The ID of the notification inbox record
        notification_raw: The raw notification data
        actor: The actor associated with the notification
        endo_reply_id: Id of the endorsement reply if applicable

    Returns:
        The created endorsement record
    """
    endorsement_service = current_app.extensions["invenio-notify"].endorsement_service

    actor_id = actor.id
    log.info(f"Found actor ID {actor_id} for actor_id '{actor.actor_id}'")

    noti_type = identify_supported_type(notification, supported=SUPPORTED_TYPES)
    if not noti_type:
        raise DataNotFound(f"Notification type not found in notification {inbox_id}")

    # Handle both string record_id and RDMRecordMetadata object
    if isinstance(record_item, str):
        record = None  # Will be queried only if needed for endorsement type
        record_id = record_item
    else:
        # record_item is RDMRecordMetadata object
        record = record_item
        record_id = str(record.id)

    review_url = None
    if notification.object:
        review_url = notification.object.cite_as
        if review_url is None:
            review_url = notification.object.id

    # Create the endorsement record data
    endorsement_data = {
        'record_id': record_id,
        'actor_id': actor_id,
        'review_type': noti_type,
        'inbox_id': inbox_id,
        'result_url': review_url,
        'actor_name': actor.name,
        'endorsement_reply_id': endo_reply_id,
    }

    # Get actor name for notification
    actor_name = actor.name

    if noti_type == constants.TYPE_ENDORSEMENT:
        # Get the record if we don't have it yet
        record = record or get_record_by_id(record_id)
        uow.register(
            NotificationOp(
                NewEndorsementNotificationBuilder.build(
                    record=record,
                    actor_name=actor_name,
                    endorsement_url=review_url,
                    user_id=get_user_id_by_record(record),
                ),
            )
        )
    elif noti_type == constants.TYPE_REVIEW:
        create_endorsement_update_notification(
            record_id,
            actor_name,
            constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW,
            uow
        )


    # Create the endorsement record
    return endorsement_service.create(identity, endorsement_data, uow=uow)
