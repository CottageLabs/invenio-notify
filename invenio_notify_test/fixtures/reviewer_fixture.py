from datetime import datetime, timezone

import pytest

from invenio_notify.records.models import ReviewerModel


@pytest.fixture
def create_reviewer(db, superuser_identity):
    """Fixture to create a ReviewerModel instance."""

    def _create_reviewer(actor_id=None, name='Test Reviewer',
                         inbox_url='https://example.com/inbox',

                         inbox_api_token=None, description=None):
        """Create a ReviewerModel instance.
        
        Args:
            actor_id: Actor ID for the reviewer (default: 'test-reviewer-id')
            name: Name of the reviewer (default: 'Test Reviewer')
            inbox_url: URL for the reviewer's inbox (default: 'https://example.com/inbox')
            inbox_api_token: Optional API token for the reviewer's inbox
            description: Optional description of the reviewer

        Returns:
            ReviewerModel instance
        """

        if actor_id is None:
            actor_id = 'test-reviewer-id-' + datetime.now(timezone.utc).isoformat()
        reviewer = ReviewerModel.create({
            'actor_id': actor_id,
            'name': name,
            'inbox_url': inbox_url,
            'inbox_api_token': inbox_api_token,
            'description': description
        })
        return reviewer

    return _create_reviewer


@pytest.fixture
def create_multiple_reviewers(db, create_reviewer):
    """Fixture to create multiple reviewers for testing."""
    def _create_multiple_reviewers(count=3):
        reviewers = []
        for i in range(count):
            reviewer = create_reviewer(
                name=f'Test Reviewer {i+1}',
                inbox_url=f'https://reviewer{i+1}.example.com/inbox',
                inbox_api_token=f'token{i+1}',
                actor_id=f'https://reviewer{i+1}.example.com'
            )
            reviewers.append(reviewer)
        return reviewers
    return _create_multiple_reviewers


def reviewer_data(actor_id='reviewer-actor-123', name='Test Reviewer',
                 inbox_url='https://example.com/inbox',
                 inbox_api_token='test-inbox-api-token', description='Test description'):
    """Generate a reviewer data dictionary.
    
    Args:
        actor_id: Actor ID for the reviewer
        name: Name of the reviewer
        inbox_url: URL for the reviewer's inbox
        inbox_api_token: Optional API token for the reviewer's inbox
        description: Description of the reviewer
        
    Returns:
        Dictionary with reviewer data
    """
    return {
        'actor_id': actor_id,
        'name': name,
        'inbox_url': inbox_url,
        'inbox_api_token': inbox_api_token,
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
            'actor_id': f'reviewer-actor-{i}',
            'name': f'Reviewer {i}',
            'inbox_url': f'https://example.com/inbox{i}',
            'inbox_api_token': f'test-token-{i}' if i % 2 == 0 else None,
            'description': f'Description for reviewer {i}'
        }
        for i in range(1, count + 1)
    ]
    return reviewers


