import pytest
import uuid
from invenio_notify.records.models import EndorsementRequestModel


def create_default_endorsement_request_data(reviewer_id, record_uuid=None, latest_status="Request Endorsement"):
    """Create default data for EndorsementRequestModel.
    
    Args:
        reviewer_id: ID of the reviewer
        record_uuid: UUID of the record (generates random if None)
        latest_status: Status of the request
        
    Returns:
        dict: Data for creating EndorsementRequestModel
    """
    return {
        'record_uuid': record_uuid or str(uuid.uuid4()),
        'reviewer_id': reviewer_id,
        'raw': {'test': 'data'},
        'latest_status': latest_status
    }


@pytest.fixture
def create_endorsement_request(superuser_identity, create_reviewer):
    """Fixture to create an endorsement request."""
    def _create_endorsement_request(record_uuid=None, reviewer_id=None, latest_status="Request Endorsement"):
        if reviewer_id is None:
            reviewer = create_reviewer()
            reviewer_id = reviewer.id
        
        if record_uuid is None:
            record_uuid = str(uuid.uuid4())
            
        return EndorsementRequestModel.create(
            create_default_endorsement_request_data(reviewer_id, record_uuid, latest_status)
        )
    return _create_endorsement_request