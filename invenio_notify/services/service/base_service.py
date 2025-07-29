import regex
from invenio_db.uow import unit_of_work
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.base.utils import map_search_params

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
    def create(self, identity, data, raise_errors=True, uow=None, schema=None):
        self.require_permission(identity, "create")

        schema = schema or self.schema

        valid_data, errors = schema.load(
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