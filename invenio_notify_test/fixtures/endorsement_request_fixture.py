import uuid

import pytest

from invenio_notify.records.models import EndorsementRequestModel


def create_endorsement_request_data(reviewer_id, record_id, latest_status="Request Endorsement", raw=None, user_id=None, noti_id=None):
    """Create default data for EndorsementRequestModel.
    
    Args:
        reviewer_id: ID of the reviewer
        record_id: UUID of the record (required)
        latest_status: Status of the request
        raw: Raw data dict (uses default if None)
        user_id: ID of the user (optional, will be auto-set by service if None)
        noti_id: Notification UUID from COAR notification (required if None will generate default)
        
    Returns:
        dict: Data for creating EndorsementRequestModel
    """
    import uuid
    data = {
        'record_id': record_id,
        'reviewer_id': reviewer_id,
        'raw': raw or {'test': 'data'},
        'latest_status': latest_status,
        'noti_id': noti_id or uuid.uuid4()
    }
    if user_id is not None:
        data['user_id'] = user_id
    return data


@pytest.fixture
def create_endorsement_request(superuser_identity, create_reviewer):
    """Fixture to create an endorsement request."""
    def _create_endorsement_request(record_id, reviewer_id=None, latest_status="Request Endorsement", user_id=None, noti_id=None):
        if reviewer_id is None:
            reviewer = create_reviewer()
            reviewer_id = reviewer.id
        
        if user_id is None:
            user_id = superuser_identity.id

        noti_id = noti_id or uuid.uuid4()
            
        return EndorsementRequestModel.create(
            create_endorsement_request_data(reviewer_id, record_id, latest_status, user_id=user_id, noti_id=noti_id)
        )
    return _create_endorsement_request