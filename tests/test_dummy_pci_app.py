import json
import pytest
from unittest.mock import patch

from invenio_notify.dummy_actor.dummy_pci_app import app
from tests.fixtures.endorsement_request_payload import payload_endorsement_request


@patch('invenio_notify.dummy_actor.dummy_pci_app.DummyPCIBackend')
class TestDummyInboxEndpoint:
    """Test the dummy inbox endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_success(self, mock_backend):
        """Test POST with valid endorsement request payload returns 200."""
        payload = payload_endorsement_request("test-record-123")

        response = self.client.post(
            '/dummy-actor/dummy-inbox',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': 'Bearer test-token'}
        )

        assert response.status_code == 202

        data = json.loads(response.data)
        assert data['status'] == 202
        assert 'message' in data

    def test_no_json(self, mock_backend):
        """Test POST without JSON returns 400."""
        response = self.client.post(
            '/dummy-actor/dummy-inbox',
            headers={'Authorization': 'Bearer test-token'}
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 400
        assert data['message'] == 'Request must be JSON'

    def test_malformed_json(self, mock_backend):
        """Test POST with malformed JSON returns 400."""
        response = self.client.post(
            '/dummy-actor/dummy-inbox',
            data='{"invalid": "json"}',
            content_type='application/json',
            headers={'Authorization': 'Bearer test-token'}
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 400
        assert 'message' in data

    def test_missing_auth_header(self, mock_backend):
        """Test POST without Authorization header returns 401."""
        payload = payload_endorsement_request("test-record-123")

        response = self.client.post(
            '/dummy-actor/dummy-inbox',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 401

        data = json.loads(response.data)
        assert data['status'] == 401
        assert data['message'] == 'Unauthorized: Missing or invalid token'
