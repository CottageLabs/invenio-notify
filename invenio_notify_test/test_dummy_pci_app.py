import json
import unittest

from invenio_notify.dummy_reviewer.dummy_pci_app import app


class TestDummyPCIAppBase(unittest.TestCase):
    """Base test class with common setup."""

    def setUp(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()


class TestDummyInboxEndpoint(TestDummyPCIAppBase):
    """Test the dummy inbox endpoint."""

    def test_post_no_json(self):
        """Test POST without JSON returns 400."""
        response = self.client.post('/dummy-reviewer/dummy-inbox')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 400)
        self.assertEqual(data['message'], 'Request must be JSON')

    def test_post_malformed_json(self):
        """Test POST with malformed JSON returns 400."""
        response = self.client.post(
            '/dummy-reviewer/dummy-inbox',
            data='{"invalid": json}',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 400)
        self.assertIn('message', data)
