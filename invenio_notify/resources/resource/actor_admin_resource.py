from flask import g
from flask_resources import (
    resource_requestctx,
    response_handler,
    route,
)
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_view_args,
)

from invenio_notify.services.schemas import ActorSchema
from .basic_db_resource import BasicDbResource


class ActorAdminResource(BasicDbResource):

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            route("POST", routes["list"], self.create),
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
            route("DELETE", routes["item"], self.delete),
            route("PUT", routes["item"], self.update),
            route("GET", routes["members"], self.get_members),
            route("POST", routes["members"], self.add_member),
            route("DELETE", routes["member"], self.del_member),
        ]

    @request_data
    @response_handler()
    def create(self):
        return self.create_with_out_id()

    @request_headers
    @request_view_args
    @request_data
    def add_member(self):
        actor = self.service.add_member(
            identity=g.identity,
            id=resource_requestctx.view_args["record_id"],
            data=resource_requestctx.data,
        )
        actor_dict = ActorSchema().dump(actor)
        return actor_dict, 201

    @request_headers
    @request_view_args
    @request_data
    def del_member(self):
        actor = self.service.del_member(
            identity=g.identity,
            id=resource_requestctx.view_args["record_id"],
            data=resource_requestctx.data,
        )
        actor_dict = ActorSchema().dump(actor)
        return actor_dict, 200

    @request_headers
    @request_view_args
    @response_handler()
    def get_members(self):
        """Get members for a actor."""
        members = self.service.get_members(
            identity=g.identity,
            id=resource_requestctx.view_args["record_id"],
        )
        return {"hits": members}, 200