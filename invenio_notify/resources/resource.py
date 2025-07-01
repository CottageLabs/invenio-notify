from flask import g
from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
)

from invenio_notify.services.schemas import ReviewerSchema

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
        reviewer = self.service.add_member(
            identity=g.identity,
            id=resource_requestctx.view_args["record_id"],
            data=resource_requestctx.data,
        )
        reviewer_dict = ReviewerSchema().dump(reviewer)
        return reviewer_dict, 201

    @request_headers
    @request_view_args
    @request_data
    def del_member(self):
        reviewer = self.service.del_member(
            identity=g.identity,
            id=resource_requestctx.view_args["record_id"],
            data=resource_requestctx.data,
        )
        reviewer_dict = ReviewerSchema().dump(reviewer)
        return reviewer_dict, 200

    @request_headers
    @request_view_args
    @response_handler()
    def get_members(self):
        """Get members for a reviewer."""
        members = self.service.get_members(
            identity=g.identity,
            id=resource_requestctx.view_args["record_id"],
        )
        return {"hits": members}, 200


class InboxApiResource(ErrorHandlersMixin, Resource):
    """Resource for handling COAR notification inbox endpoint."""

    def __init__(self, config, service):
        """Constructor."""
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
        """Create the URL rules for the inbox resource."""
        return [
            route("POST", "/notify/inbox", self.receive_notification),
        ]

    @request_data
    @response_handler()
    def receive_notification(self):
        """Receive COAR notification via POST to /inbox."""
        from flask import current_app
        from invenio_oauth2server import require_oauth_scopes, require_api_auth
        from invenio_pidstore.errors import PIDDoesNotExistError
        from coarnotify.server import COARNotifyServerError
        from invenio_notify import constants
        from invenio_notify.errors import COARProcessFail
        from invenio_notify.scopes import inbox_scope
        from invenio_notify.views.api_views import create_fail_response, response_coar_notify_receipt
        
        # Apply authentication and authorization
        require_api_auth()
        require_oauth_scopes(inbox_scope.id)
        
        data = resource_requestctx.data
        if not data:
            return create_fail_response(constants.STATUS_BAD_REQUEST, "Request must be JSON")

        try:
            result = self.service.receive_notification(data)
            return response_coar_notify_receipt(result)

        except COARNotifyServerError as e:
            current_app.logger.error(f'Error: {e.message}')
            return create_fail_response(constants.STATUS_BAD_REQUEST)

        except COARProcessFail as e:
            return create_fail_response(e.status, e.msg)

        except PIDDoesNotExistError as e:
            current_app.logger.debug(f'inbox PIDDoesNotExistError {e.pid_type}:{e.pid_value}')
            return create_fail_response(constants.STATUS_NOT_FOUND, "Record not found")