import pytest
from invenio_accounts.models import User
from invenio_notify.records.models import ReviewerModel
from invenio_notify.services.config import ReviewerServiceConfig
from invenio_notify.services.service import ReviewerService
from invenio_notify_test.utils import resolve_user_id


@pytest.fixture
def create_reviewer(db, superuser_identity):
    """Fixture to create a ReviewerModel instance."""

    def _create_reviewer(coar_id='test-reviewer-id', name='Test Reviewer',
                         inbox_url='https://example.com/inbox',
                         description=None):
        """Create a ReviewerModel instance.
        
        Args:
            coar_id: COAR ID for the reviewer (default: 'test-reviewer-id')
            name: Name of the reviewer (default: 'Test Reviewer')
            inbox_url: URL for the reviewer's inbox (default: 'https://example.com/inbox')
            description: Optional description of the reviewer

        Returns:
            ReviewerModel instance
        """

        reviewer = ReviewerModel.create({
            'coar_id': coar_id,
            'name': name,
            'inbox_url': inbox_url,
            'description': description
        })
        return reviewer

    return _create_reviewer


def reviewer_data(coar_id='reviewer-coar-123', name='Test Reviewer',
                 inbox_url='https://example.com/inbox',
                 description='Test description'):
    """Generate a reviewer data dictionary.
    
    Args:
        coar_id: COAR ID for the reviewer
        name: Name of the reviewer
        inbox_url: URL for the reviewer's inbox
        description: Description of the reviewer
        
    Returns:
        Dictionary with reviewer data
    """
    return {
        'coar_id': coar_id,
        'name': name,
        'inbox_url': inbox_url,
        'description': description
    }


def sample_reviewers(count=3):
    """Generate sample reviewer data dictionaries.
    
    Args:
        count: Number of sample reviewers to generate (default: 3)
        
    Returns:
        List of dictionaries with reviewer data
    """
    reviewers = [
        {
            'coar_id': f'reviewer-coar-{i}',
            'name': f'Reviewer {i}',
            'inbox_url': f'https://example.com/inbox{i}',
            'description': f'Description for reviewer {i}'
        }
        for i in range(1, count + 1)
    ]
    return reviewers


def create_reviewer_service() -> ReviewerService:
    from invenio_notify.proxies import current_reviewer_service
    return current_reviewer_service