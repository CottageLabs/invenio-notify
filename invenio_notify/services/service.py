import json
import regex
import urllib.parse
from flask import current_app
from flask import g
from invenio_db.uow import unit_of_work
from invenio_rdm_records.services import RDMRecordService
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.base import LinksTemplate

from coarnotify.core.notify import NotifyPattern
from coarnotify.server import COARNotifyServiceBinding, COARNotifyReceipt, COARNotifyServer

re_url_record_id = regex.compile(r'/records/(.*?)$')


class NotifyInboxService(RecordService):

    def search(self, identity, params=None, search_preference=None, expand=False, **kwargs):
        self.require_permission(identity, "search")

        params = params or {}
        # search_params = map_search_params(self.config.search, params)
        search_params = {}

        filters = []
        record_list = self.record_cls.search(search_params, filters)
        record_list = list(record_list)

        return self.result_list(
            self,
            identity,
            record_list,
            params=search_params,
            links_tpl=LinksTemplate(self.config.links_search, context={"args": params}),
            links_item_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def delete(self, identity, id, uow=None):
        """Delete a banner from database."""
        self.require_permission(identity, "delete")

        record = self.record_cls.get(id)
        self.record_cls.delete(record)

        return self.result_item(self, identity, record, links_tpl=self.links_item_tpl)

    def read(self, identity, id):
        self.require_permission(identity, "read")

        record = self.record_cls.get(id)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def create(self, identity, data, raise_errors=True, uow=None):
        self.require_permission(identity, "create")

        data['user_id'] = identity.id

        # validate data
        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        record = self.record_cls.create(valid_data)

        return self.result_item(
            self, identity, record, links_tpl=self.links_item_tpl, errors=errors
        )

    def receive_notification(self, notification_raw: dict):
        server = COARNotifyServer(InvnotiCOARNotifyServiceBinding())
        current_app.logger.debug(f'input announcement:')
        result = server.receive(notification_raw, validate=True)
        current_app.logger.debug(f'result: {result}')
        return result


def get_record_id_by_record_url(record_url: str) -> str:
    url_path = urllib.parse.urlparse(record_url).path
    record_id = re_url_record_id.match(url_path)
    return record_id and record_id.group(1)


class InvnotiCOARNotifyServiceBinding(COARNotifyServiceBinding):

    def notification_received(self, notification: NotifyPattern) -> COARNotifyReceipt:
        current_app.logger.debug('called notification_received')

        raw = notification.to_jsonld()
        record_id = get_record_id_by_record_url(raw['context']['id'])

        # check if record exists
        records_service: RDMRecordService = current_app.extensions["invenio-rdm-records"].records_service
        records_service.record_cls.pid.resolve(record_id)  # raises PIDDoesNotExistError if not found

        current_app.logger.debug(f'client input raw: {raw}')
        inbox_service: NotifyInboxService = current_app.extensions["invenio-notify"].notify_inbox_service
        inbox_service.create(g.identity, {"raw": json.dumps(raw), 'record_id': record_id})

        location = 'http://127.0.0.1/tobeimplemented'  # KTODO implement this
        return COARNotifyReceipt(COARNotifyReceipt.CREATED, location)


class EndorsementService(RecordService):
    pass
