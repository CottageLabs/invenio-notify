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
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_view_args,
)
from invenio_records_resources.services.records.results import RecordItem

from invenio_notify import constants
from invenio_notify.errors import SendRequestFail, BadRequestError
from invenio_notify.records.models import ReviewerModel, EndorsementRequestModel
from invenio_notify.utils import record_utils, endorsement_request_utils
from invenio_notify.utils.endorsement_request_utils import (
    create_endorsement_request_data,
    get_available_reviewers,
    can_send
)
from invenio_notify.utils.record_utils import resolve_record_from_pid
from invenio_rdm_records.records import RDMRecord
from ..errors import ApiErrorHandlersMixin


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
        "notification_id": endorsement_request_data["id"],
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
    """
    Resource for handling endorsement requests.

    Api that used by frontend landing page "Endorsement Request" section.
    """

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

        validate_owner_id(record._record, user.id)

        endo_status = endorsement_request_utils.get_overall_endorsement_status(record._record.model.id, reviewer_id)
        if not can_send(endo_status, reviewer):
            raise BadRequestError('Reviewer not available for endorsement request')

        endorsement_request_data = create_endorsement_request_data(user, record, reviewer)
        send_to_reviewer_inbox(reviewer, endorsement_request_data)

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

        validate_owner_id(record, user_id)

        reviewers = get_available_reviewers(record.id)
        return reviewers, 200