"""Utilities for invenio-notify tests."""


def resolve_user_id(user_id=None, identity=None, default_identity=None):
    """Resolve a user_id from either a direct ID or an identity object.
    
    Args:
        user_id: User ID (takes precedence if provided)
        identity: Identity object to get user_id from
        default_identity: Default identity to use if neither user_id nor identity is provided
        
    Returns:
        Resolved user_id
    """
    if user_id is None:
        if identity is None:
            identity = default_identity
        user_id = identity.id
    return user_id
