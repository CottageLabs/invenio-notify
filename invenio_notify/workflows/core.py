#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.
import logging
from datetime import datetime, timezone
from typing import Optional

from invenio_db.uow import unit_of_work
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.records.models import RDMRecordMetadata, RDMParentMetadata

from invenio_rdm_records.proxies import current_rdm_records_service

from invenio_rdm_records.records import RDMRecord

from invenio_notify.records.models import NotifyInboxModel
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
    inbox_record.process_date = datetime.now(timezone.utc)
    if comment is not None:
        inbox_record.process_note = comment

class DataNotFound(Exception):
    """Custom exception for when notification processing fails due to missing or invalid data."""

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)
        self.message = message


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