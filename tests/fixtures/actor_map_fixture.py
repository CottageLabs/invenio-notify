import pytest

from invenio_notify.records.models import ActorMapModel
from tests.fixtures.actor_fixture import create_actor
from tests.utils import resolve_user_id


@pytest.fixture
def create_actor_map(db, superuser_identity, create_actor):
    """Fixture to create a ActorMapModel instance."""
    def _create_actor_map(actor_id=None, user_id=None, identity=None):
        """Create a ActorMapModel instance.
        
        Args:
            actor_id: External actor ID (default: 'external-actor-123')
            user_id: User ID to associate with the actor (overrides identity)
            identity: Identity object to get user_id from (defaults to superuser_identity)
            
        Returns:
            ActorMapModel instance
        """

        user_id = resolve_user_id(user_id, identity, superuser_identity)
        actor = create_actor(actor_id=actor_id)

        actor_map = ActorMapModel.create({
            'actor_id': actor.id,
            'user_id': user_id
        })
        return actor_map
    return _create_actor_map


def create_actor_map_dict(actor_id, user_id):
    """Create a dictionary representing a actor map.

    Args:
        actor_id: External actor identifier
        user_id: Internal user identifier

    Returns:
        Dict with actor_id and user_id
    """
    return {
        'actor_id': actor_id,
        'user_id': user_id
    }
