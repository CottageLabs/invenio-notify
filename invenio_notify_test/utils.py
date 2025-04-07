"""Utilities for invenio-notify tests."""
import pytest
from invenio_db import db

from invenio_notify.errors import NotExistsError


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


class BasicDbServiceTestHelper:
    """Base class for database service test helpers.
    
    This class provides common test methods for database-backed (non index db) services.
    
    Abstract methods:
        _create_service: Create and return the service instance to test
        _create_record: Create and return a test record using the provided identity
        
    Test methods:
        test_delete: Tests successful record deletion
        test_delete__not_exists: Tests error handling for non-existent records
        test_search: Tests search functionality with and without filters
    """

    def _create_service(self):
        raise NotImplementedError()

    def _create_record(self, identity):
        """Create a test record.
        
        Args:
            identity: The identity to use for creation
            
        Returns:
            The created record
        """
        raise NotImplementedError()

    def test_delete(self, superuser_identity):
        """Test the successful deletion of a record."""
        service = self._create_service()

        # Create a record to delete
        record: db.Model = self._create_record(superuser_identity)
        record_id = record.id

        assert record.query.get(record_id) is not None

        # Delete the record
        service.delete(superuser_identity, record_id)

        # Verify the record no longer exists
        with pytest.raises(NotExistsError):
            service.delete(superuser_identity, record_id)

    def test_delete__not_exists(self, superuser_identity):
        service = self._create_service()
        with pytest.raises(NotExistsError):
            service.delete(superuser_identity, 999999)

    def test_search(self, superuser_identity):
        """Test basic search functionality with and without filters."""

        sample_size = 3

        service = self._create_service()

        # Create multiple test records
        for i in range(sample_size):
            self._create_record(superuser_identity)

        # Search without parameters should return all records
        result = service.search(superuser_identity)
        result_list = result.to_dict()['hits']['hits']
        assert len(result_list) >= sample_size  # Should find at least our 3 records
