import json
import pytest

from invenio_notify.dummy_reviewer.dummy_pci_app import app
from invenio_notify_test.fixtures.endorsement_request_payload import payload_endorsement_request


class TestDummyInboxEndpoint:
    """Test the dummy inbox endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_success(self):
        """Test POST with valid endorsement request payload returns 200."""
        payload = payload_endorsement_request("test-record-123")

        response = self.client.post(
            '/dummy-reviewer/dummy-inbox',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 202

        data = json.loads(response.data)
        assert data['status'] == 202
        assert 'message' in data

    def test_no_json(self):
        """Test POST without JSON returns 400."""
        response = self.client.post('/dummy-reviewer/dummy-inbox')

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 400
        assert data['message'] == 'Request must be JSON'

    def test_malformed_json(self):
        """Test POST with malformed JSON returns 400."""
        response = self.client.post(
            '/dummy-reviewer/dummy-inbox',
            data='{"invalid": "json"}',
            content_type='application/json'
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 400
        assert 'message' in data
