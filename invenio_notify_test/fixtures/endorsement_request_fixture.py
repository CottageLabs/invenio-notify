import uuid

import pytest

from invenio_notify.records.models import EndorsementRequestModel


def create_endorsement_request_data(reviewer_id, record_id=None, latest_status="Request Endorsement", raw=None):
    """Create default data for EndorsementRequestModel.
    
    Args:
        reviewer_id: ID of the reviewer
        record_id: UUID of the record (generates random if None)
        latest_status: Status of the request
        raw: Raw data dict (uses default if None)
        
    Returns:
        dict: Data for creating EndorsementRequestModel
    """
    return {
        'record_id': record_id or str(uuid.uuid4()),
        'reviewer_id': reviewer_id,
        'raw': raw or {'test': 'data'},
        'latest_status': latest_status
    }


@pytest.fixture
def create_endorsement_request(superuser_identity, create_reviewer):
    """Fixture to create an endorsement request."""
    def _create_endorsement_request(record_id=None, reviewer_id=None, latest_status="Request Endorsement"):
        if reviewer_id is None:
            reviewer = create_reviewer()
            reviewer_id = reviewer.id
        
        if record_id is None:
            record_id = str(uuid.uuid4())
            
        return EndorsementRequestModel.create(
            create_endorsement_request_data(reviewer_id, record_id, latest_status)
        )
    return _create_endorsement_request