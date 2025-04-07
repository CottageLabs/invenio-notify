import pytest
from invenio_notify.records.models import ReviewerMapModel
from invenio_notify_test.utils import resolve_user_id


@pytest.fixture
def create_reviewer_map(db, superuser_identity):
    """Fixture to create a ReviewerMapModel instance."""
    def _create_reviewer_map(reviewer_id='external-reviewer-123', user_id=None, identity=None):
        """Create a ReviewerMapModel instance.
        
        Args:
            reviewer_id: External reviewer ID (default: 'external-reviewer-123')
            user_id: User ID to associate with the reviewer (overrides identity)
            identity: Identity object to get user_id from (defaults to superuser_identity)
            
        Returns:
            ReviewerMapModel instance
        """
        user_id = resolve_user_id(user_id, identity, superuser_identity)
            
        reviewer_map = ReviewerMapModel.create({
            'reviewer_id': reviewer_id,
            'user_id': user_id
        })
        return reviewer_map
    return _create_reviewer_map
