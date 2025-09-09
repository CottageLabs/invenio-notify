from flask import current_app
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
from invenio_notify.tasks import get_notification_type
from invenio_notify.utils.notify_utils import get_recid_by_record_url
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services import RDMRecordService
from .base_service import BasicDbService
from sqlalchemy import or_, cast, String


def get_record_id_from_notification(raw: dict) -> str:
    """Extract record ID from notification data.

    Args:
        raw (dict): Raw notification data

    Returns:
        str: Record ID extracted from notification

    Raises:
        COARProcessFail: If no record URL is found
    """
    record_url = None
    if raw.get('context', {}).get('id'):
        record_url = raw['context']['id']
    elif raw.get('object', {}).get('object', {}).get('id'):
        record_url = raw['object']['object']['id']

    if not record_url:
        current_app.logger.error('No record URL found in notification')
        raise COARProcessFail(constants.STATUS_BAD_REQUEST, 'No record URL found')

    return get_recid_by_record_url(record_url)


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

    def receive_notification(self, notification_raw: dict, identity) -> COARNotifyReceipt:
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

        raw = notification.to_jsonld()
        record_id = get_record_id_from_notification(raw)

        notification_id = raw.get('id')
        if not notification_id:
            current_app.logger.error('Missing notification ID in COAR notification')
            raise COARProcessFail(constants.STATUS_BAD_REQUEST, 'Missing notification ID')

        actor_id = raw['actor']['id']
        if not ActorModel.has_member(self._identity.id, actor_id):
            current_app.logger.warning(f'Actor id not match with user: {actor_id}, {self._identity.id}')
            raise COARProcessFail(constants.STATUS_FORBIDDEN, 'Actor Id mismatch')

        if not get_notification_type(raw):
            current_app.logger.info(f'Unknown type: [{record_id=}]{raw.get("type")}')
            raise COARProcessFail(constants.STATUS_NOT_ACCEPTED, 'Notification type not supported')

        records_service: RDMRecordService = current_rdm_records_service
        records_service.record_cls.pid.resolve(record_id)

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
