#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from flask import current_app, g
from idutils.normalizers import normalize_doi
from idutils.validators import is_doi
from invenio_access.permissions import system_identity
from invenio_db.uow import unit_of_work
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from coarnotify.core.notify import NotifyPattern
from coarnotify.server import (
    COARNotifyReceipt,
    COARNotifyServer,
    COARNotifyServiceBinding,
)
from invenio_notify import constants
from invenio_notify.errors import COARProcessFail
from invenio_notify.proxies import current_inbox_service
from invenio_notify.records.models import ActorModel
from invenio_notify.utils.notify_utils import get_recid_by_record_url
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services import RDMRecordService
from .base_service import BasicDbService
from sqlalchemy import or_, cast, String


class NotifyInboxService(BasicDbService):

    def _create_search_filters(self, query_param):
        """Create search filters based on the query parameter."""
        filters = []
        if query_param and query_param.strip():
            search_term = f"%{query_param.strip()}%"
            model = self.record_cls

            # Search across multiple fields
            search_conditions = [
                model.notification_id.cast(String).ilike(search_term),  # Search in notification ID
                model.record_id.ilike(search_term),  # Search in record ID
                model.process_note.ilike(search_term),  # Search in process notes
                cast(model.raw, String).ilike(search_term),  # Search in raw JSON data
            ]

            filters.append(or_(*search_conditions))

        return filters

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        return super().search(identity, params, search_preference, expand, filter_maker=self._create_search_filters,
                              **kwargs)

    def receive_notification(self, identity, notification_raw: dict) -> COARNotifyReceipt:
        """Process a COAR notification with injected identity.

        Args:
            notification_raw: The raw notification data
            identity: The identity object
            
        Returns:
            COARNotifyReceipt indicating processing result
        """
        server = COARNotifyServer(InboxCOARBinding(identity))
        current_app.logger.debug(f'input announcement:')
        result = server.receive(notification_raw, validate=True)
        current_app.logger.debug(f'result: {result}')
        return result

    @property
    def schema_api(self):
        return ServiceSchemaWrapper(self, schema=self.config.schema_api)

    @unit_of_work()
    def create(self, identity, data, raise_errors=True, uow=None):
        data['user_id'] = identity.id

        if 'notification_id' not in data and 'raw' in data:
            raw = data['raw']
            notification_id = raw.get('id')
            if notification_id:
                data['notification_id'] = notification_id
            else:
                current_app.logger.error('Missing notification ID in raw data')
                raise ValueError('Missing notification ID in raw data')

        return super().create(
            identity,
            data,
            raise_errors=raise_errors,
            uow=uow,
            schema=self.schema_api
        )

    def get_record_id_from_notification(self, notification: NotifyPattern) -> str:
        """Extract record ID from notification data.

        Args:
            raw (dict): Raw notification data

        Returns:
            str: Record ID extracted from notification

        Raises:
            COARProcessFail: If no record URL is found
        """
        # Try each location the record URL may appear, in order of preference:
        # 1. context.id (Announce-type patterns: AnnounceReview, AnnounceEndorsement)
        # 2. object.object.id (reply-type patterns: TentativeAccept, Reject, TentativeReject —
        #    notification.object is a nested NotifyPattern via NestedPatternObjectMixin, and
        #    its .object holds the record reference)
        # 3. object.id (fallback)
        record_url = None
        ctx = notification.context
        if ctx is not None:
            record_url = ctx.id
        if record_url is None:
            obj = notification.object
            if obj is not None:
                nested_obj = obj.object if hasattr(obj, 'object') else None
                if nested_obj is not None:
                    record_url = nested_obj.id
                if record_url is None:
                    record_url = obj.id

        if not record_url:
            current_app.logger.error('No record URL found in notification')
            raise COARProcessFail(constants.STATUS_BAD_REQUEST, 'No record URL found')

        # Check if record_url is a DOI
        if is_doi(record_url):
            # Extract the normalized DOI from the URI
            normalized_doi = normalize_doi(record_url)
            pids_service = current_rdm_records.records_service.pids

            try:
                record = pids_service.resolve(system_identity, normalized_doi, "doi")
                return record["id"]
            except PIDDoesNotExistError as e:
                current_app.logger.error(f'No record with the DOI {record_url} exists: {e}')
            except Exception as e:
                current_app.logger.error(f'Unexpected error while searching for records with DOI {record_url}: {e}')

        return get_recid_by_record_url(record_url)


class InboxCOARBinding(COARNotifyServiceBinding):
    """COAR notification binding with injectable identity."""
    
    def __init__(self, identity):
        """Initialize with identity.
        
        Args:
            identity: The identity object.
        """
        super().__init__()
        self._identity = identity

    def notification_received(self, notification: NotifyPattern) -> COARNotifyReceipt:
        current_app.logger.debug('called notification_received')

        # raw = notification.to_jsonld()
        record_id = current_inbox_service.get_record_id_from_notification(notification)

        # notification_id = raw.get('id')
        notification_id = notification.id
        if not notification_id:
            current_app.logger.error('Missing notification ID in COAR notification')
            raise COARProcessFail(constants.STATUS_BAD_REQUEST, 'Missing notification ID')

        # actor_id = raw['actor']['id']
        actor_id = notification.actor.id
        if not ActorModel.has_member(self._identity.id, actor_id):
            current_app.logger.warning(f'Actor ID did not match with user: {actor_id}, {self._identity.id}')
            raise COARProcessFail(constants.STATUS_FORBIDDEN, 'Actor Id mismatch')

        records_service: RDMRecordService = current_rdm_records_service
        records_service.record_cls.pid.resolve(record_id)

        raw = notification.to_jsonld()
        current_app.logger.debug(f'client input raw: {raw}')
        try:
            inbox_record = {"notification_id": notification_id, "raw": raw, 'record_id': record_id}
            current_inbox_service.create(self._identity, inbox_record)
        except IntegrityError as e:
            # Check if it's specifically a unique constraint violation
            if hasattr(e.orig, 'pgcode') and e.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
                current_app.logger.warning(f'Duplicate notification_id {notification_id}: {e}')
                raise COARProcessFail(constants.STATUS_BAD_REQUEST, f'Notification already exists: {notification_id}')
            else:
                # Re-raise other integrity errors (foreign key, check constraints, etc.)
                current_app.logger.error(f'Database integrity error: {e}')
                raise COARProcessFail(constants.STATUS_BAD_REQUEST, f'Database integrity error')
        except Exception as e:
            current_app.logger.error(f'Failed to create inbox record: {e}')
            raise COARProcessFail(constants.STATUS_BAD_REQUEST, f'Failed to create inbox record')

        return COARNotifyReceipt(COARNotifyReceipt.ACCEPTED)

