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
from invenio_notify.records.models import ActorModel, EndorsementRequestModel, EndorsementModel
from invenio_notify.utils import record_utils
from invenio_notify.utils.endorsement_request_utils import (
    create_endorsement_request_data,
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
def create_endorsement_request_record(endorsement_request_data, record_id, user_id, actor_id, uow=None):
    """Create endorsement request database record.
    
    Args:
        endorsement_request_data: Dictionary containing endorsement request data
        record_id: ID of the record
        user_id: ID of the user making the request
        actor_id: ID of the actor
        
    Returns:
        EndorsementRequestModel: The created endorsement request record
    """
    return EndorsementRequestModel.create({
        "notification_id": endorsement_request_data["id"],
        "record_id": record_id,
        "user_id": user_id,
        "actor_id": actor_id,
        "raw": endorsement_request_data,
        "latest_status": constants.WORKFLOW_STATUS_REQUEST_ENDORSEMENT,
    })


def send_to_actor_inbox(actor, endorsement_request_data: dict):
    """Send endorsement request to actor's inbox.
    
    Args:
        actor: ActorModel instance
        endorsement_request_data: Dictionary containing endorsement request data
        
    Returns:
        str: Error message if validation fails, None if successful
    """
    if not actor.inbox_url:
        current_app.logger.error(
            f'Actor inbox URL is not configured for actor {actor.id} url[{actor.inbox_url}]'
        )
        raise ValueError('Actor inbox URL is not configured')

    try:
        response = requests.post(
            actor.inbox_url,
            json=endorsement_request_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {actor.inbox_api_token}',
            },
            timeout=30
        )

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Failed to send request to actor inbox: {e}')
        raise SendRequestFail('Failed to send request')

    if response.status_code not in {200, 201, 202}:
        current_app.logger.warning(
            f'Actor inbox request failed with '
            f'status code [{response.status_code}] for actor [{actor.inbox_url}]'
            f' -- {response.text}'
        )
        raise SendRequestFail('Actor reply invalid request', status=response.status_code)

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
            route("GET", self.config.routes["actors"], self.list_actors, ),
        ]

    @request_view_args
    @request_data
    @response_handler()
    def send(self):
        """Send endorsement request."""
        data = resource_requestctx.data
        pid_value = resource_requestctx.view_args["pid_value"]

        if not data or 'actor_id' not in data:
            raise ValueError('actor_id is required')
        if g.identity is None or g.identity.id is None:
            raise BadRequestError('User identity is required')

        actor_id = data['actor_id']

        actor = ActorModel.query.filter_by(id=actor_id).one()

        if not actor or not actor.inbox_url or not actor.inbox_api_token:
            raise BadRequestError('Actor not available for endorsement request')

        record: RecordItem = record_utils.read_record_item(system_identity, pid_value)
        user = User.query.get(g.identity.id)

        validate_owner_id(record._record, user.id)

        record_id = record._record.model.id

        # First check if there's an actual endorsement
        status = EndorsementModel.get_latest_status(record_id, actor_id)
        if status:
            raise BadRequestError(f'Actor not available for endorsement request')

        # If no endorsement, check endorsement request status
        status = EndorsementRequestModel.get_latest_status(record_id, actor_id)

        # If there is a previous request, only allow if the status is TentativeReject
        if status and status != constants.WORKFLOW_STATUS_TENTATIVE_REJECT:
            raise BadRequestError(f'Actor not available for endorsement request')

        endorsement_request_data = create_endorsement_request_data(user, record, actor)
        send_to_actor_inbox(actor, endorsement_request_data)

        try:
            create_endorsement_request_record(endorsement_request_data, record._record.model.id, user.id, actor_id)
            current_app.logger.info(f'Created endorsement request record for actor {actor_id}')
        except Exception as e:
            current_app.logger.error(f'Failed to create endorsement request record: {e}')
            raise Exception('Failed to create endorsement request record') from e

        return {'is_success': 1, 'message': 'Request Accepted'}, 200

    @request_view_args
    @response_handler()
    def list_actors(self):
        """List all available actors."""
        pid_value = resource_requestctx.view_args["pid_value"]
        record = resolve_record_from_pid(pid_value)

        if g.identity is None or g.identity.id is None:
            raise BadRequestError('User identity is required')

        user_id = g.identity.id

        validate_owner_id(record, user_id)

        actors = ActorModel.get_available_actors(record.id)
        return actors, 200