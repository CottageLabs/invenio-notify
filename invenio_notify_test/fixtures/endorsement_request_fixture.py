import uuid

import pytest

from invenio_notify.records.models import EndorsementRequestModel
from invenio_notify_test.conftest import prepare_test_rdm_record


def create_endorsement_request_data(reviewer_id, record_id=None, latest_status="Request Endorsement", raw=None, user_id=None, db=None, minimal_record=None):
    """Create default data for EndorsementRequestModel.
    
    Args:
        reviewer_id: ID of the reviewer
        record_id: UUID of the record (creates test record if None and db/minimal_record provided)
        latest_status: Status of the request
        raw: Raw data dict (uses default if None)
        user_id: ID of the user (optional, will be auto-set by service if None)
        db: Database session (needed if record_id is None)
        minimal_record: Minimal record data (needed if record_id is None)
        
    Returns:
        dict: Data for creating EndorsementRequestModel
    """
    if record_id is None:
        # KTODO if else does not needed
        if db is not None and minimal_record is not None:
            record = prepare_test_rdm_record(db, minimal_record)
            record_id = record.id
        else:
            record_id = str(uuid.uuid4())
    
    data = {
        'record_id': record_id,
        'reviewer_id': reviewer_id,
        'raw': raw or {'test': 'data'},
        'latest_status': latest_status
    }
    if user_id is not None:
        data['user_id'] = user_id
    return data


@pytest.fixture
def create_endorsement_request(superuser_identity, create_reviewer, db, minimal_record):
    """Fixture to create an endorsement request."""
    def _create_endorsement_request(record_id=None, reviewer_id=None, latest_status="Request Endorsement", user_id=None):
        if reviewer_id is None:
            reviewer = create_reviewer()
            reviewer_id = reviewer.id
        
        if record_id is None:
            record = prepare_test_rdm_record(db, minimal_record)
            record_id = record.id
        
        if user_id is None:
            user_id = superuser_identity.id
            
        return EndorsementRequestModel.create(
            create_endorsement_request_data(reviewer_id, record_id, latest_status, user_id=user_id)
        )
    return _create_endorsement_request