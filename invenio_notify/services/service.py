import json
import regex
from flask import current_app
from flask import g
from invenio_db.uow import unit_of_work
from invenio_rdm_records.services import RDMRecordService
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.base.utils import map_search_params
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper

from coarnotify.core.notify import NotifyPattern
from coarnotify.server import COARNotifyServiceBinding, COARNotifyReceipt, COARNotifyServer
from invenio_notify import constants
from invenio_notify.errors import COARProcessFail
from invenio_notify.records.models import ReviewerMapModel, ReviewerModel
from invenio_notify.utils import user_utils
from invenio_notify.utils.notify_utils import get_recid_by_record_url

re_url_record_id = regex.compile(r'/records/(.*?)$')


class BasicDbService(RecordService):

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        self.require_permission(identity, "search")

        params = params or {}

        search_params = map_search_params(self.config.search, params)
        query_param = search_params["q"]

        filters = []
        if filter_maker:
            filters.extend(filter_maker(query_param))

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

    @unit_of_work()
    def update(self, identity, id, data, uow=None):
        self.require_permission(identity, "update")

        record = self.record_cls.get(id)

        # validate data
        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=True,
        )

        self.record_cls.update(valid_data, id)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )


class NotifyInboxService(BasicDbService):

    @unit_of_work()
    def create(self, identity, data, raise_errors=True, uow=None):
        data['user_id'] = identity.id
        return super().create(identity, data, raise_errors=raise_errors, uow=uow)

    def receive_notification(self, notification_raw: dict) -> COARNotifyReceipt:
        server = COARNotifyServer(InboxCOARBinding())
        current_app.logger.debug(f'input announcement:')
        result = server.receive(notification_raw, validate=True)
        current_app.logger.debug(f'result: {result}')
        return result


class InboxCOARBinding(COARNotifyServiceBinding):

    def notification_received(self, notification: NotifyPattern) -> COARNotifyReceipt:
        current_app.logger.debug('called notification_received')

        raw = notification.to_jsonld()
        recid = get_recid_by_record_url(raw['context']['id'])

        # Check actor_id match with user
        actor_id = raw['actor']['id']
        if not ReviewerModel.has_member(g.identity.id, actor_id):
            current_app.logger.warning(f'Actor id not match with user: {actor_id}, {g.identity.id}')
            raise COARProcessFail(constants.STATUS_FORBIDDEN, 'Actor Id mismatch')

        # Check if the notification type is supported
        if all(t not in constants.REVIEW_TYPES for t in raw.get('type', [])):
            current_app.logger.info(f'Unknown type: [{recid=}]{raw.get("type")}')
            raise COARProcessFail(constants.STATUS_NOT_ACCEPTED, 'Notification type not supported')

        # check if record exists
        records_service: RDMRecordService = current_app.extensions["invenio-rdm-records"].records_service
        records_service.record_cls.pid.resolve(recid)  # raises PIDDoesNotExistError if not found

        current_app.logger.debug(f'client input raw: {raw}')
        inbox_service: NotifyInboxService = current_app.extensions["invenio-notify"].notify_inbox_service
        inbox_service.create(g.identity, {"raw": json.dumps(raw), 'recid': recid})

        return COARNotifyReceipt(COARNotifyReceipt.ACCEPTED)


class EndorsementService(RecordService):
    pass


class ReviewerMapService(BasicDbService):

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        if filter_maker is None:
            def filter_maker(query_param):
                filters = []
                if query_param:
                    filters.extend([
                        self.record_cls.reviewer_id == query_param,
                    ])
                return filters

        return super().search(identity, params, search_preference, expand, filter_maker, **kwargs)


class ReviewerService(BasicDbService):
    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        if filter_maker is None:
            def filter_maker(query_param):
                filters = []
                if query_param:
                    filters.extend([
                        self.record_cls.name.ilike(f'%{query_param}%'),
                    ])
                return filters

        return super().search(identity, params, search_preference, expand, filter_maker, **kwargs)

    @property
    def schema_add_member(self):
        return ServiceSchemaWrapper(self, schema=self.config.schema_add_member)

    @unit_of_work()
    def add_member(self, identity, id, data, raise_errors=True, uow=None):
        self.require_permission(identity, "update")

        reviewer: ReviewerModel = self.record_cls.get(id)

        # validate data
        valid_data, errors = self.schema_add_member.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        new_emails = set(valid_data['emails'])
        existing_emails = {m.email for m in reviewer.members}
        duplicate_emails = new_emails.intersection(existing_emails)
        if duplicate_emails:
            current_app.logger.info(f'Emails already exist: {duplicate_emails}')

        new_emails = new_emails - existing_emails
        if not new_emails:
            current_app.logger.info('No new emails to add')
            return reviewer

        added_members = []
        for email in new_emails:
            user = user_utils.find_user_by_email(email)
            if user:
                current_app.logger.info(f'Adding user [{user.email}] to reviewer [{reviewer.coar_id}]')
                ReviewerMapModel.create({
                    'user_id': user.id,
                    'reviewer_id': reviewer.id
                })
                added_members.append(user)
            else:
                current_app.logger.warning(f'User with email {email} not found')
        
        reviewer = self.record_cls.get(id)
        return reviewer
