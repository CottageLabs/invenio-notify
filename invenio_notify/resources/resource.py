from flask_resources import Resource


from flask import g
from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
)

from .errors import ErrorHandlersMixin


class NotifyInboxResource(ErrorHandlersMixin, Resource):

    def __init__(self, config, service):
        """Constructor."""
        super(NotifyInboxResource, self).__init__(config)
        self.service = service

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

    # @request_view_args
    # @request_data
    # @response_handler()
    # def update(self):
    #     """Update a raw notification."""
    #     raw_noti = self.service.update(
    #         id=resource_requestctx.view_args["rawnoti_id"],
    #         identity=g.identity,
    #         data=resource_requestctx.data,
    #     )
    #
    #     # disable expired notifications
    #     self.service.disable_expired(identity=g.identity)
    #
    #     return raw_noti.to_dict(), 200

    @request_view_args
    @response_handler()
    def read(self):
        """Read a notify inbox."""
        notify_inbox_id = resource_requestctx.view_args["notify_inbox_id"]
        result_item = self.service.read(
            id=notify_inbox_id,
            identity=g.identity,
        )
        return result_item.to_dict(), 200

    @request_search_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the notify inboxes."""
        result_list = self.service.search(
            identity=g.identity,
            params=resource_requestctx.args,
        )
        return result_list.to_dict(), 200

    # @request_data
    # @response_handler()
    # def create(self):
    #     """Create a raw notification."""
    #     raw_noti = self.service.create(
    #         g.identity,
    #         resource_requestctx.data or {},
    #         )
    #
    #     # disable expired notifications
    #     self.service.disable_expired(identity=g.identity)
    #
    #     return raw_noti.to_dict(), 201

    @request_headers
    @request_view_args
    def delete(self):
        """Delete a raw notification."""
        notify_inbox_id = resource_requestctx.view_args["notify_inbox_id"]
        raw_noti = self.service.delete(
            id=notify_inbox_id,
            identity=g.identity,
        )

        return raw_noti.to_dict(), 204
