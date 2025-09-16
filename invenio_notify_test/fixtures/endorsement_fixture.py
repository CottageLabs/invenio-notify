"""Fixtures for endorsement-related tests."""

import pytest

from invenio_notify import constants
from invenio_notify.records.models import EndorsementModel


@pytest.fixture
def create_endorsement(db):
    """Factory fixture to create endorsements.
    
    Args:
        record_id: ID of the record being endorsed
        actor_id: ID of the actor entity
        inbox_id: ID of the notification inbox
        review_type: Type of review (default: endorsement)
        result_url: URL of the review result
        
    Returns:
        function: A factory function to create endorsements
    """

    def _create_endorsement(
            record_id,
            actor_id,
            inbox_id=None,
            review_type=constants.TYPE_ENDORSEMENT,
            result_url="https://example.com/result",
            actor_name="Test Actor"
    ):
        """Create an endorsement."""
        data = {
            'record_id': record_id,
            'actor_id': actor_id,
            'review_type': review_type,
            'inbox_id': inbox_id,
            'result_url': result_url,
        }
        
        data['actor_name'] = actor_name

        model = EndorsementModel()
        model.create(data)
        model.commit()
        return model

    yield _create_endorsement
