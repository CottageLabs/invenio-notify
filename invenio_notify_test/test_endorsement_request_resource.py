from unittest.mock import patch, Mock

from invenio_records_resources.services.records.results import RecordItem

from invenio_notify.resources.resource import endorsement_request_resource
from invenio_notify_test.fixtures.reviewer_fixture import create_multiple_reviewers
from invenio_notify_test.fixtures.user_fixture import different_user


class TestListReviewers:
    """Test class for EndorsementRequestResource.list_reviewers endpoint."""

    @staticmethod
    def send_list_reviewers(client, identity, record=None, record_id=None):
        """Helper method to make request with mocked g.identity and resolve_record_from_pid."""
        actual_record_id = record_id or record.id
        url = f'/api/endorsement-request/reviewers/{actual_record_id}'

        with patch.object(endorsement_request_resource, 'g') as mock_g:
            mock_g.identity = identity
            if record:
                with patch.object(endorsement_request_resource, 'resolve_record_from_pid') as mock_resolve:
                    mock_resolve.return_value = record._record
                    return client.get(url)
            else:
                return client.get(url)

    def test_success(self, client, rdm_record, superuser_identity, create_multiple_reviewers, db):
        """Test successful retrieval of available reviewers by record owner."""
        create_multiple_reviewers(2)

        # Ensure the superuser is the owner
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id

        response = self.send_list_reviewers(client, superuser_identity, rdm_record, rdm_record.id)

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_unauthorized_user(self, client, rdm_record, superuser_identity, different_user, create_multiple_reviewers,
                               db):
        """Test that non-owner cannot access reviewers list."""
        create_multiple_reviewers(1)

        # Set record owner to different user
        rdm_record._record.parent.access.owner.owner_id = different_user.id

        response = self.send_list_reviewers(client, superuser_identity, rdm_record, rdm_record.id)

        assert response.status_code == 400
        data = response.get_json()
        assert 'User is not the owner of this record' in data.get('message', '')

    def test_invalid_record_id(self, client, superuser_identity, create_multiple_reviewers):
        """Test request with non-existent record ID."""
        create_multiple_reviewers(1)

        response = self.send_list_reviewers(client, superuser_identity, None, 'non-existent-record')

        assert response.status_code == 404

    def test_no_available_reviewers(self, client, rdm_record, superuser_identity):
        """Test when no reviewers are available."""
        # Ensure the superuser is the owner
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id

        response = self.send_list_reviewers(client, superuser_identity, rdm_record, rdm_record.id)

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_unauthenticated_request(self, client, rdm_record, create_multiple_reviewers):
        """Test request without authentication."""
        create_multiple_reviewers(1)

        response = self.send_list_reviewers(client, None, rdm_record, rdm_record.id)

        # The API actually returns a handled error response, not 500
        # Based on the actual behavior, it should return a client error
        assert response.status_code == 400


class TestSend:
    """Test class for EndorsementRequestResource.send endpoint."""

    @staticmethod
    def send_endorsement_request(client, identity, record: RecordItem, reviewer_id):
        """Helper method to make endorsement request with mocked g.identity and current_rdm_records_service.read."""
        url = f'/api/endorsement-request/send/{record.id}'
        # from unittest.mock import AsyncMock, patch

        with patch.object(endorsement_request_resource, 'g') as mock_g:
            mock_g.identity = identity
            with patch.object(endorsement_request_resource.record_utils, 'read_record_item') as mock_read:
                mock_read.return_value = record
                # mock_read.read = AsyncMock(return_value=record)
                return client.post(url, json={"reviewer_id": reviewer_id})

    @patch.object(endorsement_request_resource.requests, 'post')
    def test_success(self, mock_post, client, rdm_record, superuser_identity, create_reviewer, db):
        """Test successful endorsement request."""
        # Create reviewer with proper configuration
        reviewer = create_reviewer(
            name='Test Reviewer',
            inbox_url='https://example.com/inbox',
            inbox_api_token='test-token'
        )

        # Set up record ownership
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id

        # Mock successful external request
        mock_post.return_value = Mock(status_code=200)

        response = self.send_endorsement_request(client, superuser_identity, rdm_record, reviewer.id)

        assert response.status_code == 200
        data = response.get_json()
        assert data['is_success'] == 1
        assert 'Request Accepted' in data['message']

        # Verify external request was made
        mock_post.assert_called_once()

    def test_missing_reviewer_id(self, client, rdm_record, superuser_identity):
        """Test request without reviewer_id field."""
        url = f'/api/endorsement-request/send/{rdm_record.id}'

        with patch('invenio_notify.resources.resource.endorsement_request_resource.g') as mock_g:
            mock_g.identity = superuser_identity
            with patch(
                    'invenio_notify.resources.resource.endorsement_request_resource.resolve_record_from_pid') as mock_resolve:
                mock_resolve.return_value = rdm_record._record
                response = client.post(url, json={})

        assert response.status_code == 400

    def test_invalid_reviewer_id(self, client, rdm_record, superuser_identity):
        """Test request with non-existent reviewer ID."""
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id

        response = self.send_endorsement_request(client, superuser_identity, rdm_record, 99999)

        assert response.status_code == 404

    def test_unauthorized_user(self, client, rdm_record, superuser_identity, different_user, create_reviewer, db):
        """Test that non-owner cannot send endorsement request."""
        reviewer = create_reviewer(
            inbox_api_token='test-token',
        )

        # Set record owner to different user
        rdm_record._record.parent.access.owner.owner_id = different_user.id

        response = self.send_endorsement_request(client, superuser_identity, rdm_record, reviewer.id)

        assert response.status_code == 400
        data = response.get_json()
        assert 'User is not the owner of this record' in data.get('message', '')

    def test_invalid_reviewer(self, client, rdm_record, superuser_identity, create_reviewer, db):
        """Test that non-owner cannot send endorsement request."""
        reviewer = create_reviewer(
            inbox_url=None,
            inbox_api_token=None,
        )

        # Set record owner to different user
        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id

        response = self.send_endorsement_request(client, superuser_identity, rdm_record, reviewer.id)

        assert response.status_code == 400
        assert 'Reviewer not available for endorsement request' in response.get_json().get('message', '')

    def test_unauthenticated_request(self, client, rdm_record, create_reviewer):
        """Test request without authentication."""
        reviewer = create_reviewer()

        response = self.send_endorsement_request(client, None, rdm_record, reviewer.id)

        assert response.status_code == 400

    @patch.object(endorsement_request_resource.requests, 'post')
    def test_reviewer_inbox_request_fails(self, mock_post, client, rdm_record, superuser_identity, create_reviewer, db):
        """Test handling of reviewer inbox request failure."""
        reviewer = create_reviewer(
            inbox_url='https://example.com/inbox',
            inbox_api_token='test-token'
        )

        rdm_record._record.parent.access.owner.owner_id = superuser_identity.user.id

        # Mock failed external request
        mock_post.return_value = Mock(status_code=500, text='Internal Server Error')

        response = self.send_endorsement_request(client, superuser_identity, rdm_record, reviewer.id)

        assert response.status_code == 400
