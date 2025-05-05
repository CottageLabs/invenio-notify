from flask import g
from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
)

from .errors import ErrorHandlersMixin


class BasicDbResource(ErrorHandlersMixin, Resource):

    def __init__(self, config, service):
        """Constructor."""
        super().__init__(config)
        self.service = service

    @request_view_args
    @response_handler()
    def read(self):
        """Read a notify inbox."""
        result_item = self.service.read(
            id=resource_requestctx.view_args["record_id"],
            identity=g.identity,
        )
        return result_item.to_dict(), 200

    @request_search_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the notify inboxes."""
        result_list = self.service.search(
            params=resource_requestctx.args,
            identity=g.identity,
        )
        return result_list.to_dict(), 200

    @request_headers
    @request_view_args
    def delete(self):
        """Delete a raw notification."""
        result_item = self.service.delete(
            id=resource_requestctx.view_args["record_id"],
            identity=g.identity,
        )

        return result_item.to_dict(), 204

    @request_view_args
    @request_data
    @response_handler()
    def update(self):
        record = self.service.update(
            id=resource_requestctx.view_args["record_id"],
            identity=g.identity,
            data=resource_requestctx.data,
        )

        return record.to_dict(), 200

    @request_data
    @response_handler()
    def create(self):
        record = self.service.create(
            g.identity,
            resource_requestctx.data or {},
        )

        return record.to_dict(), 201

    def create_with_out_id(self):
        resource_requestctx.data.pop('id', None)
        record = self.service.create(
            g.identity,
            resource_requestctx.data or {},
        )

        return record.to_dict(), 201


class NotifyInboxResource(BasicDbResource):

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            # route("POST", routes["list"], self.create),
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
            route("DELETE", routes["item"], self.delete),
            # route("PUT", routes["item"], self.update),
        ]


class ReviewerMapResource(BasicDbResource):

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            route("POST", routes["list"], self.create),
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
            route("DELETE", routes["item"], self.delete),
            route("PUT", routes["item"], self.update),
        ]

    @request_data
    @response_handler()
    def create(self):
        return self.create_with_out_id()


class ReviewerResource(BasicDbResource):

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            route("POST", routes["list"], self.create),
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
            route("DELETE", routes["item"], self.delete),
            route("PUT", routes["item"], self.update),
            route("POST", routes["add-member"], self.add_member),
        ]

    @request_data
    @response_handler()
    def create(self):
        return self.create_with_out_id()

    @request_headers
    @request_view_args
    @request_data
    def add_member(self):
        self.service.add_member(
            identity=g.identity,
            id=resource_requestctx.view_args["record_id"],
            data=resource_requestctx.data,
        )
        return {}, 200
