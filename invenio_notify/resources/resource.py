import requests
from flask import g, current_app
from flask_resources import (
    Resource,
    resource_requestctx,
    response_handler,
    route, create_error_handler,
)
from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_db.uow import unit_of_work
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.services.records.results import RecordItem

from coarnotify.server import COARNotifyServerError
from invenio_notify import constants
from invenio_notify.errors import COARProcessFail, SendRequestFail, BadRequestError
from invenio_notify.records.models import ReviewerModel, EndorsementRequestModel
from invenio_notify.services.schemas import ReviewerSchema
from invenio_notify.utils.endorsement_request_utils import create_endorsement_request_data, get_available_reviewers, \
    get_latest_endorsement_request, can_send
from invenio_notify.utils.notify_response import response_coar_notify_receipt, create_default_msg_by_status
from invenio_notify.utils.record_utils import resolve_record_from_pid
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.resources.errors import HTTPJSONException
from .errors import ErrorHandlersMixin, ApiErrorHandlersMixin, create_error_handler_with_json
from ..utils import record_utils


# KTODO add Admin page for Endorsement Requests
# KTODO refactor to make resource become a package, all Resource should be a module in a package


def validate_owner_id(record: RDMRecord, user_id):
    """Check if the user is the owner of the record.
    
    Args:
        record: RDMRecord instance
        user_id: ID of the user to check
        
    Raises:
        BadRequestError: If user is not the record owner
    """
    if record.parent.access.owner.owner_id != user_id:
        raise BadRequestError('User is not the owner of this record')


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
        # TODO catch and handle exception if actor id is not url
        data = resource_requestctx.data

        if not data:
            raise ValueError("Request data is required")

        result = self.service.receive_notification(notification_raw=data)
        return response_coar_notify_receipt(result)


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
        "noti_id": endorsement_request_data["id"].replace('urn:uuid:', ''),
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
        raise ValueError('Reviewer inbox URL is not configured')

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
        raise SendRequestFail('Failed to send request')

    if response.status_code not in {200, 201, 202}:
        current_app.logger.warning(
            f'Reviewer inbox request failed with '
            f'status code [{response.status_code}] for reviewer [{reviewer.inbox_url}]'
            f' -- {response.text}'
        )
        raise SendRequestFail('Reviewer reply invalid request', status=response.status_code)

    return None


class EndorsementRequestResource(ApiErrorHandlersMixin, Resource):
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

        if not data or 'reviewer_id' not in data:
            raise ValueError('reviewer_id is required')
        if g.identity is None or g.identity.id is None:
            raise BadRequestError('User identity is required')

        reviewer_id = data['reviewer_id']

        reviewer = ReviewerModel.query.filter_by(id=reviewer_id).one()
        record: RecordItem = record_utils.read_record_item(system_identity, pid_value)
        user = User.query.get(g.identity.id)

        # Check if user is the record owner
        validate_owner_id(record._record, user.id)

        # Check if reviewer is available using can_send logic
        endorsement_request = get_latest_endorsement_request(record._record.model.id, reviewer_id, user.id)
        if not can_send(endorsement_request, reviewer):
            raise BadRequestError('Reviewer not available for endorsement request')

        # Get origin_id from config
        origin_id = current_app.config.get("NOTIFY_ORIGIN_ID", None)
        if not origin_id:
            raise ValueError("NOTIFY_ORIGIN_ID must be set in invenio.cfg")

        # Send endorsement request to reviewer's inbox
        endorsement_request_data = create_endorsement_request_data(user, record, reviewer, origin_id)
        send_to_reviewer_inbox(reviewer, endorsement_request_data)

        # Create endorsement request record
        try:
            create_endorsement_request_record(endorsement_request_data, record._record.model.id, user.id, reviewer_id)
            current_app.logger.info(f'Created endorsement request record for reviewer {reviewer_id}')
        except Exception as e:
            current_app.logger.error(f'Failed to create endorsement request record: {e}')
            raise Exception('Failed to create endorsement request record') from e

        return {'is_success': 1, 'message': 'Request Accepted'}, 200

    @request_view_args
    @response_handler()
    def list_reviewers(self):
        """List all available reviewers."""
        pid_value = resource_requestctx.view_args["pid_value"]
        record = resolve_record_from_pid(pid_value)

        if g.identity is None or g.identity.id is None:
            raise BadRequestError('User identity is required')

        user_id = g.identity.id

        # Check if user is the record owner
        validate_owner_id(record, user_id)

        reviewers = get_available_reviewers(record.id, user_id)
        return reviewers, 200
