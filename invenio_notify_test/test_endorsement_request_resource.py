from unittest.mock import patch

import pytest
from invenio_accounts.models import User

from invenio_notify_test.fixtures.reviewer_fixture import create_multiple_reviewers


class TestListReviewers:
    """Test class for EndorsementRequestResource.list_reviewers endpoint."""

    @pytest.fixture
    def different_user(self, db):
        """Create a different user for non-owner tests."""
        user = User(email='different@example.com', username='different_user')
        db.session.add(user)
        db.session.commit()
        return user

    def test_success(self, client, rdm_record, superuser_identity, create_multiple_reviewers, db):
        """Test successful retrieval of available reviewers by record owner."""
        create_multiple_reviewers(2)
        
        # Ensure the superuser is the owner
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id
        
        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = superuser_identity
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}'
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_unauthorized_user(self, client, rdm_record, superuser_identity, different_user, create_multiple_reviewers, db):
        """Test that non-owner cannot access reviewers list."""
        create_multiple_reviewers(1)
        
        # Set record owner to different user
        rdm_record._record.parent.access.owner.owner_id = different_user.id

        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = superuser_identity
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}'
            )

        assert response.status_code == 400
        data = response.get_json()
        assert 'User is not the owner of this record' in data.get('message', '')

    def test_invalid_record_id(self, client, superuser_identity, create_multiple_reviewers):
        """Test request with non-existent record ID."""
        create_multiple_reviewers(1)
        
        with patch('invenio_notify.resources.resource.g') as mock_g:
            mock_g.identity = superuser_identity
            response = client.get(
                '/api/endorsement-request/reviewers/non-existent-record'
            )
        
        assert response.status_code == 404

    def test_no_available_reviewers(self, client, rdm_record, superuser_identity):
        """Test when no reviewers are available."""
        # Ensure the superuser is the owner
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id
        
        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = superuser_identity
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}'
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_unauthenticated_request(self, client, rdm_record, create_multiple_reviewers):
        """Test request without authentication."""
        create_multiple_reviewers(1)
        
        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = None
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}'
            )
        
        # The API actually returns a handled error response, not 500
        # Based on the actual behavior, it should return a client error
        assert response.status_code == 400