from flask_resources import (
    Resource,
    resource_requestctx,
    response_handler,
    route,
)
from invenio_records_resources.resources.records.resource import request_data

from coarnotify.server import COARNotifyServerError
from invenio_notify.errors import COARProcessFail
from invenio_notify.utils.notify_response import response_coar_notify_receipt, create_default_msg_by_status
from invenio_rdm_records.resources.errors import HTTPJSONException
from ..errors import ApiErrorHandlersMixin, create_error_handler_with_json, create_error_handler


def require_inbox_oauth():
    """Decorator that requires OAuth authentication with inbox scope."""

    def decorator(f):
        from invenio_oauth2server import require_oauth_scopes, require_api_auth
        from invenio_notify.scopes import inbox_scope

        f = require_oauth_scopes(inbox_scope.id)(f)
        f = require_api_auth()(f)
        return f

    return decorator


class InboxApiResource(Resource):
    """Resource for handling COAR notification inbox endpoint."""

    error_handlers = {
        **ApiErrorHandlersMixin.error_handlers,
        COARNotifyServerError: create_error_handler_with_json(400, lambda e: create_default_msg_by_status(400)),
        COARProcessFail: create_error_handler(
            lambda e: HTTPJSONException(
                code=e.status,
                description=e.description
            )
        )
    }

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
    @require_inbox_oauth()
    def receive_notification(self):
        """Receive COAR notification via POST to /inbox."""
        data = resource_requestctx.data

        if not data:
            raise ValueError("Request data is required")

        result = self.service.receive_notification(notification_raw=data)
        return response_coar_notify_receipt(result)