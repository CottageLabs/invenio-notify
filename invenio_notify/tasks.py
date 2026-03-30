#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

import logging

from celery import shared_task
from coarnotify.factory import COARNotifyFactory

from invenio_notify.records.models import NotifyInboxModel, ActorModel

from invenio_notify.workflows import endorsement
from invenio_notify.workflows.core import mark_as_processed, DataNotFound

# Workflows available for notify
WORKFLOWS = [endorsement]

log = logging.getLogger(__name__)

def get_actor_by_actor_id(notification_raw: dict) -> ActorModel:
    """
    Extract actor data from notification by actor ID.
    
    Args:
        notification_raw: The raw notification data
        
    Returns:
        ActorModel if found
        
    Raises:
        DataNotFound: If actor ID is not found or actor doesn't exist
    """
    # Extract actor ID from notification
    actor_id = notification_raw.get('actor', {}).get('id', None)
    if not actor_id:
        raise DataNotFound(f"Actor ID not found in notification, actor[{actor_id}]")

    # Find ActorModel with matching actor_id
    actor = ActorModel.query.filter_by(actor_id=actor_id).first()
    if not actor:
        raise DataNotFound(f"Actor not found, actor_id[{actor_id}]")

    return actor


def inbox_processing():
    for workflow in WORKFLOWS:
        for inbox_record in NotifyInboxModel.unprocessed_records():
            try:
                notification = COARNotifyFactory.get_by_object(inbox_record.raw)
                notification_raw: dict = notification.to_jsonld()
            except Exception as e:
                msg = f"Failed to decode inbox json {inbox_record.id}: {e}"
                log.error(msg)
                mark_as_processed(inbox_record, msg)
                continue

            # Get actor using the utility function
            try:
                actor = get_actor_by_actor_id(notification_raw)
            except DataNotFound as e:
                log.warning(f"Failed to get actor: {e}")
                mark_as_processed(inbox_record, e.message)
                continue

            # Check if noti sender is a member of the actor
            if not ActorModel.has_member(inbox_record.user_id, actor.actor_id):
                log.warning(f"User {inbox_record.user_id} is not a member of actor {actor.actor_id}")
                mark_as_processed(inbox_record, "User is not a member of actor")
                continue

            try:
                workflow.process_next_notification(inbox_record, notification, actor)
            except Exception as e:
                mark_as_processed(inbox_record, "an unspecified error occurred processing the notification")



@shared_task
def shared_task_inbox_processing():
    inbox_processing()
