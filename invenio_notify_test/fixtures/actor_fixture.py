from datetime import datetime, timezone

import pytest

from invenio_notify.records.models import ActorModel


@pytest.fixture
def create_actor(db, superuser_identity):
    """Fixture to create a ActorModel instance."""

    def _create_actor(actor_id=None, name='Test Actor',
                         inbox_url='https://example.com/inbox',

                         inbox_api_token=None, description=None):
        """Create a ActorModel instance.
        
        Args:
            actor_id: Actor ID for the actor (default: 'test-actor-id')
            name: Name of the actor (default: 'Test Actor')
            inbox_url: URL for the actor's inbox (default: 'https://example.com/inbox')
            inbox_api_token: Optional API token for the actor's inbox
            description: Optional description of the actor

        Returns:
            ActorModel instance
        """

        if actor_id is None:
            actor_id = 'test-actor-id-' + datetime.now(timezone.utc).isoformat()
        actor = ActorModel.create({
            'actor_id': actor_id,
            'name': name,
            'inbox_url': inbox_url,
            'inbox_api_token': inbox_api_token,
            'description': description
        })
        return actor

    return _create_actor


@pytest.fixture
def create_multiple_actors(db, create_actor):
    """Fixture to create multiple actors for testing."""
    def _create_multiple_actors(count=3):
        actors = []
        for i in range(count):
            actor = create_actor(
                name=f'Test Actor {i+1}',
                inbox_url=f'https://actor{i+1}.example.com/inbox',
                inbox_api_token=f'token{i+1}',
                actor_id=f'https://actor{i+1}.example.com'
            )
            actors.append(actor)
        return actors
    return _create_multiple_actors


def actor_data(actor_id='actor-actor-123', name='Test Actor',
                 inbox_url='https://example.com/inbox',
                 inbox_api_token='test-inbox-api-token', description='Test description'):
    """Generate a actor data dictionary.
    
    Args:
        actor_id: Actor ID for the actor
        name: Name of the actor
        inbox_url: URL for the actor's inbox
        inbox_api_token: Optional API token for the actor's inbox
        description: Description of the actor
        
    Returns:
        Dictionary with actor data
    """
    return {
        'actor_id': actor_id,
        'name': name,
        'inbox_url': inbox_url,
        'inbox_api_token': inbox_api_token,
        'description': description
    }


def sample_actors(count=3):
    """Generate sample actor data dictionaries.
    
    Args:
        count: Number of sample actors to generate (default: 3)
        
    Returns:
        List of dictionaries with actor data
    """
    actors = [
        {
            'actor_id': f'actor-actor-{i}',
            'name': f'Actor {i}',
            'inbox_url': f'https://example.com/inbox{i}',
            'inbox_api_token': f'test-token-{i}' if i % 2 == 0 else None,
            'description': f'Description for actor {i}'
        }
        for i in range(1, count + 1)
    ]
    return actors


