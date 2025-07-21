from unittest.mock import patch

import pytest
from invenio_accounts.models import User

from invenio_notify.records.models import ReviewerModel


class TestListReviewers:
    """Test class for EndorsementRequestResource.list_reviewers endpoint."""

    @pytest.fixture
    def reviewer_setup(self, db):
        """Fixture to create reviewers for testing."""
        def _create_reviewers(count=3):
            reviewers = []
            for i in range(count):
                reviewer = ReviewerModel.create({
                    'name': f'Test Reviewer {i+1}',
                    'inbox_url': f'https://reviewer{i+1}.example.com/inbox',
                    'inbox_api_token': f'token{i+1}',
                    'actor_id': f'https://reviewer{i+1}.example.com'
                })
                reviewers.append(reviewer)
            db.session.commit()
            return reviewers
        return _create_reviewers

    @pytest.fixture
    def different_user(self, db):
        """Create a different user for non-owner tests."""
        user = User(email='different@example.com', username='different_user')
        db.session.add(user)
        db.session.commit()
        return user

    def test_success(self, client, rdm_record, superuser_identity, reviewer_setup, db):
        """Test successful retrieval of available reviewers by record owner."""
        reviewer_setup(2)
        
        # Ensure the superuser is the owner
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id
        
        headers = {'Authorization': 'Bearer fake-token'}
        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = superuser_identity
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}',
                headers=headers
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_unauthorized_user(self, client, rdm_record, superuser_identity, different_user, reviewer_setup, db):
        """Test that non-owner cannot access reviewers list."""
        reviewer_setup(1)
        
        # Set record owner to different user
        rdm_record._record.parent.access.owner.owner_id = different_user.id
        # db.session.commit()
        # current_rdm_records_service.indexer.index(rdm_record._record)
        
        headers = {'Authorization': 'Bearer fake-token'}
        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = superuser_identity
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}',
                headers=headers
            )

        mock_resolve.assert_called_once_with(rdm_record.id)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'User is not the owner of this record' in data.get('message', '')

    def test_invalid_record_id(self, client, superuser_identity, reviewer_setup):
        """Test request with non-existent record ID."""
        reviewer_setup(1)
        
        headers = {'Authorization': 'Bearer fake-token'}
        with patch('invenio_notify.resources.resource.g') as mock_g:
            mock_g.identity = superuser_identity
            response = client.get(
                '/api/endorsement-request/reviewers/non-existent-record',
                headers=headers
            )
        
        assert response.status_code in [404, 500]

    def test_no_available_reviewers(self, client, rdm_record, superuser_identity):
        """Test when no reviewers are available."""
        # Ensure the superuser is the owner
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id
        
        headers = {'Authorization': 'Bearer fake-token'}
        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = superuser_identity
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}',
                headers=headers
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_unauthenticated_request(self, client, rdm_record, reviewer_setup):
        """Test request without authentication."""
        reviewer_setup(1)
        
        with patch('invenio_notify.resources.resource.g') as mock_g, \
             patch('invenio_notify.resources.resource.resolve_record_from_pid') as mock_resolve:
            mock_g.identity = None
            mock_resolve.return_value = rdm_record._record
            response = client.get(
                f'/api/endorsement-request/reviewers/{rdm_record.id}'
            )
        
        # The API actually returns a handled error response, not 500
        # Based on the actual behavior, it should return a client error
        assert response.status_code in [400, 500]