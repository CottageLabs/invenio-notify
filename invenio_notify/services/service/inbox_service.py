from flask import current_app
from flask import g
from invenio_db.uow import unit_of_work
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from idutils import is_doi

from coarnotify.core.notify import NotifyPattern
from coarnotify.server import (
    COARNotifyReceipt,
    COARNotifyServer,
    COARNotifyServiceBinding,
)
from invenio_notify import constants
from invenio_notify.errors import COARProcessFail
from invenio_notify.proxies import current_inbox_service
from invenio_notify.records.models import ReviewerModel
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

    # Check if noti_id is possibly a DOI
    if is_doi(record_url):
        current_app.logger.info(f'Notification ID appears to be a DOI: {record_url}')

    # Search for records with this DOI in their metadata
    records_service: RDMRecordService = current_rdm_records_service
    try:
        # Try multiple search patterns for DOI fields
        search_queries = [
            f'metadata.identifiers.identifier:"{record_url}"',  # In identifiers array
            f'pids.doi.identifier:"{record_url}"',  # In PIDs
            f'metadata.doi:"{record_url}"',  # Direct DOI field
            f'"{record_url}"'  # Full-text search fallback
        ]

        search_results = None
        for query in search_queries:
            try:
                search_results = records_service.search(
                    g.identity,
                    params={'q': query}
                )
                if search_results.total > 0:
                    current_app.logger.info(
                        f'Found {search_results.total} record(s) with DOI {record_url} using query: {query}')
                    for hit in search_results.hits:
                        current_app.logger.debug(f'Found record with ID: {hit["id"]}')
                        return hit["id"]
                    break  # Stop searching once we find matches
            except Exception as query_error:
                current_app.logger.debug(f'Search query failed: {query} - {query_error}')
                continue

        if not search_results or search_results.total == 0:
            current_app.logger.warning(f'No records found with DOI: {record_url}')

    except Exception as e:
        current_app.logger.error(f'Failed to search for records with DOI {record_url}: {e}')

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
                model.noti_id.cast(String).ilike(search_term),  # Search in notification ID
                model.recid.ilike(search_term),  # Search in record ID
                model.process_note.ilike(search_term),  # Search in process notes
                cast(model.raw, String).ilike(search_term),  # Search in raw JSON data
            ]

            filters.append(or_(*search_conditions))

        return filters

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        return super().search(identity, params, search_preference, expand, filter_maker=self._create_search_filters,
                              **kwargs)

    def receive_notification(self, notification_raw: dict) -> COARNotifyReceipt:
        server = COARNotifyServer(InboxCOARBinding())
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

        if 'noti_id' not in data and 'raw' in data:
            raw = data['raw']
            noti_id = raw.get('id')
            if noti_id:
                data['noti_id'] = noti_id
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

    def notification_received(self, notification: NotifyPattern) -> COARNotifyReceipt:
        current_app.logger.debug('called notification_received')

        raw = notification.to_jsonld()
        recid = get_record_id_from_notification(raw)

        noti_id = raw.get('id')
        if not noti_id:
            current_app.logger.error('Missing notification ID in COAR notification')
            raise COARProcessFail(constants.STATUS_BAD_REQUEST, 'Missing notification ID')

        actor_id = raw['actor']['id']
        if not ReviewerModel.has_member(g.identity.id, actor_id):
            current_app.logger.warning(f'Actor id not match with user: {actor_id}, {g.identity.id}')
            raise COARProcessFail(constants.STATUS_FORBIDDEN, 'Actor Id mismatch')

        if not get_notification_type(raw):
            current_app.logger.info(f'Unknown type: [{recid=}]{raw.get("type")}')
            raise COARProcessFail(constants.STATUS_NOT_ACCEPTED, 'Notification type not supported')

        records_service: RDMRecordService = current_rdm_records_service
        records_service.record_cls.pid.resolve(recid)

        current_app.logger.debug(f'client input raw: {raw}')
        try:
            current_inbox_service.create(g.identity, {"noti_id": noti_id, "raw": raw, 'recid': recid})
        except Exception as e:
            current_app.logger.error(f'Failed to create inbox record: {e}')
            raise COARProcessFail(constants.STATUS_BAD_REQUEST, f'Failed to create inbox record')

        return COARNotifyReceipt(COARNotifyReceipt.ACCEPTED)