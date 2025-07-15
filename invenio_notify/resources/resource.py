import requests
from flask import g, current_app
from flask_resources import (
    Resource,
    resource_requestctx,
    response_handler,
    route,
)
from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_db.uow import unit_of_work
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.services.records.results import RecordItem

from coarnotify.server import COARNotifyServerError
from invenio_notify import constants
from invenio_notify.errors import COARProcessFail
from invenio_notify.records.models import ReviewerModel, EndorsementRequestModel
from invenio_notify.services.schemas import ReviewerSchema
from invenio_notify.utils.endorsement_request_utils import create_endorsement_request_data, get_available_reviewers, \
    get_latest_endorsement_request, can_send
from invenio_notify.utils.notify_response import create_fail_response, response_coar_notify_receipt
from invenio_notify.utils.record_utils import resolve_record_from_pid
from invenio_rdm_records.proxies import current_rdm_records_service
from .errors import ErrorHandlersMixin


def require_inbox_oauth():
    """Decorator that requires OAuth authentication with inbox scope."""

    def decorator(f):
        from invenio_oauth2server import require_oauth_scopes, require_api_auth
        from invenio_notify.scopes import inbox_scope

        # Apply decorators in correct order
        f = require_oauth_scopes(inbox_scope.id)(f)
        f = require_api_auth()(f)
        return f

    return decorator


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
    @require_inbox_oauth()
    def receive_notification(self):
        """Receive COAR notification via POST to /inbox."""
        # TODO catch and handle exception if actor id is not url
        data = resource_requestctx.data

        if not data:
            return create_fail_response(constants.STATUS_BAD_REQUEST, "Request must be JSON")

        try:
            result = self.service.receive_notification(notification_raw=data)
            return response_coar_notify_receipt(result)

        except COARNotifyServerError as e:
            current_app.logger.error(f'Error: {e.message}')
            return create_fail_response(constants.STATUS_BAD_REQUEST)

        except COARProcessFail as e:
            return create_fail_response(e.status, e.msg)

        except PIDDoesNotExistError as e:
            current_app.logger.debug(f'inbox PIDDoesNotExistError {e.pid_type}:{e.pid_value}')
            return create_fail_response(constants.STATUS_NOT_FOUND, "Record not found")


@unit_of_work()
def create_endorsement_request_record(endorsement_request_data, record_id, user_id, reviewer_id, uow=None):
    """Create endorsement request database record.
    
    Args:
        endorsement_request_data: Dictionary containing endorsement request data
        record_id: ID of the record
        user_id: ID of the user making the request
        reviewer_id: ID of the reviewer
        
    Returns:
        EndorsementRequestModel: The created endorsement request record
    """
    return EndorsementRequestModel.create({
        "noti_id": endorsement_request_data["id"],
        "record_id": record_id,
        "user_id": user_id,
        "reviewer_id": reviewer_id,
        "raw": endorsement_request_data,
        "latest_status": constants.STATUS_REQUEST_ENDORSEMENT,
    })


def send_to_reviewer_inbox(reviewer, endorsement_request_data: dict):
    """Send endorsement request to reviewer's inbox.
    
    Args:
        reviewer: ReviewerModel instance
        endorsement_request_data: Dictionary containing endorsement request data
        
    Returns:
        str: Error message if validation fails, None if successful
    """
    if not reviewer.inbox_url or not reviewer.inbox_url.startswith('http'):
        current_app.logger.error(
            f'Reviewer inbox URL is not configured for reviewer {reviewer.id} url[{reviewer.inbox_url}]'
        )
        return 'Reviewer inbox URL not configured'

    try:
        response = requests.post(
            reviewer.inbox_url,
            json=endorsement_request_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {reviewer.inbox_api_token}',
            },
            timeout=30
        )

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Failed to send request to reviewer inbox: {e}')
        return 'Failed to send request'

    if response.status_code not in {200, 201, 202}:
        # KTODO should not return status code to frontend
        return f'Request failed: {response.status_code}'

    return None


class EndorsementRequestResource(ErrorHandlersMixin, Resource):
    """Resource for handling endorsement requests."""

    def create_url_rules(self):
        """Create the URL rules for the endorsement request resource."""
        return [
            route("POST", self.config.routes["send"], self.send, ),
            route("GET", self.config.routes["reviewers"], self.list_reviewers, ),
        ]

    @request_view_args
    @request_data
    @response_handler()
    def send(self):
        """Send endorsement request."""
        data = resource_requestctx.data
        pid_value = resource_requestctx.view_args["pid_value"]

        # KTODO add permission checking
        # KTODO request can be only sent by a record owner

        if not data or 'reviewer_id' not in data:
            return {'is_success': 0, 'message': 'reviewer_id is required'}, 400

        reviewer_id = data['reviewer_id']

        # Check if reviewer exists
        reviewer = ReviewerModel.query.filter_by(id=reviewer_id).first()
        if not reviewer:
            return {'is_success': 0, 'message': 'Reviewer not found'}, 404

        # Get the record through service
        try:
            record: RecordItem = current_rdm_records_service.read(system_identity, pid_value)
        except PIDDoesNotExistError:
            return {'is_success': 0, 'message': 'Record not found'}, 404

        user = User.query.get(g.identity.id)

        # Check if reviewer is available using can_send logic
        endorsement_request = get_latest_endorsement_request(record._record.model.id, reviewer_id, user.id)
        if not can_send(endorsement_request, reviewer):
            return {'is_success': 0, 'message': 'Reviewer not available for endorsement request'}, 400

        # Send endorsement request to reviewer's inbox
        endorsement_request_data = create_endorsement_request_data(user, record)
        error_message = send_to_reviewer_inbox(reviewer, endorsement_request_data)
        if error_message:
            return {'is_success': 0, 'message': error_message}, 400

        # Create endorsement request record
        try:
            create_endorsement_request_record(endorsement_request_data, record._record.model.id, user.id, reviewer_id)
            current_app.logger.info(f'Created endorsement request record for reviewer {reviewer_id}')
        except Exception as e:
            current_app.logger.error(f'Failed to create endorsement request record: {e}')
            return {'is_success': 0, 'message': 'Failed to create endorsement request record'}, 500

        return {'is_success': 1, 'message': 'Request Accepted'}, 200

    @request_view_args
    @response_handler()
    def list_reviewers(self):
        """List all available reviewers."""
        # KTODO implement permission checking

        pid_value = resource_requestctx.view_args["pid_value"]
        try:
            record = resolve_record_from_pid(pid_value)
        except PIDDoesNotExistError:
            return {'error': 'Record not found'}, 404

        user_id = g.identity.id
        reviewers = get_available_reviewers(record.id, user_id)
        return reviewers, 200
