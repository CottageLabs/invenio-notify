import json
import unittest
from unittest.mock import patch

from coarnotify.server import COARNotifyReceipt
from invenio_notify.dummy_reviewer.dummy_pci_app import app, DummyInboxCOARBinding


class TestDummyPCIAppBase(unittest.TestCase):
    """Base test class with common setup."""
    
    def setUp(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        self.valid_notification = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://purl.org/coar/notify"
            ],
            "id": "urn:uuid:0370c0fb-bb78-4a9b-87f5-bed307a509dd",
            "type": ["Offer", "coar-notify:ReviewAction"],
            "actor": {
                "id": "https://example.org/reviewer/123",
                "type": "Service",
                "name": "Review Service"
            },
            "object": {
                "id": "https://example.org/preprint/1",
                "type": "Document"
            },
            "target": {
                "id": "https://example.org/inbox/",
                "type": "Service"
            },
            "context": {
                "id": "https://example.org/records/12345",
                "type": "Document"
            }
        }
        
        self.invalid_notification = {
            "id": "urn:uuid:0370c0fb-bb78-4a9b-87f5-bed307a509dd",
            "type": "Offer"
        }

#
# class TestDummyInboxCOARBinding(TestDummyPCIAppBase):
#     """Test the DummyInboxCOARBinding class."""
#
#     def test_notification_received_with_dict(self):
#         """Test notification_received with dict data."""
#         binding = DummyInboxCOARBinding()
#
#         with patch('builtins.print') as mock_print:
#             receipt = binding.notification_received(self.valid_notification)
#
#             self.assertIsInstance(receipt, COARNotifyReceipt)
#             self.assertEqual(receipt.status, COARNotifyReceipt.ACCEPTED)
#
#             # Verify logging calls
#             mock_print.assert_called()
#
#     def test_notification_received_with_notify_pattern(self):
#         """Test notification_received with NotifyPattern object."""
#         binding = DummyInboxCOARBinding()
#
#         # Create mock NotifyPattern object
#         class MockNotifyPattern:
#             def to_jsonld(self):
#                 return test_instance.valid_notification
#
#         test_instance = self
#
#         mock_notification = MockNotifyPattern()
#
#         with patch('builtins.print') as mock_print:
#             receipt = binding.notification_received(mock_notification)
#
#             self.assertIsInstance(receipt, COARNotifyReceipt)
#             self.assertEqual(receipt.status, COARNotifyReceipt.ACCEPTED)
#
#             # Verify logging calls
#             mock_print.assert_called()
#

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
    
    def test_post_null_json(self):
        """Test POST with null JSON returns 400."""
        response = self.client.post(
            '/dummy-reviewer/dummy-inbox',
            data=json.dumps(None),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 400)
        self.assertEqual(data['message'], 'Request must be JSON')
    
    def test_post_any_json_gets_processed(self):
        """Test that any JSON gets processed by COARNotifyServer."""
        # Test with simple JSON that will likely fail COAR validation
        simple_json = {"test": "data"}
        
        response = self.client.post(
            '/dummy-reviewer/dummy-inbox',
            data=json.dumps(simple_json),
            content_type='application/json'
        )
        
        # Should return 400 due to COAR validation failure, but proves JSON processing works
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 400)
        self.assertIn('message', data)


class TestDummyInboxCOARBindingIntegration(TestDummyPCIAppBase):
    """Test integration with DummyInboxCOARBinding."""
    
    def test_binding_returns_accepted(self):
        """Test that the binding always returns accepted."""
        binding = DummyInboxCOARBinding()
        
        # Test with any data
        test_data = {"test": "notification"}
        
        with patch('builtins.print') as mock_print:
            receipt = binding.notification_received(test_data)
            
            self.assertIsInstance(receipt, COARNotifyReceipt)
            self.assertEqual(receipt.status, COARNotifyReceipt.ACCEPTED)
            
            # Verify logging was called
            mock_print.assert_called()
    
    def test_binding_handles_notify_pattern(self):
        """Test that the binding handles NotifyPattern objects."""
        binding = DummyInboxCOARBinding()
        
        # Create mock NotifyPattern object
        class MockNotifyPattern:
            def to_jsonld(self):
                return {"id": "test", "type": "test"}
        
        mock_notification = MockNotifyPattern()
        
        with patch('builtins.print') as mock_print:
            receipt = binding.notification_received(mock_notification)
            
            self.assertIsInstance(receipt, COARNotifyReceipt)
            self.assertEqual(receipt.status, COARNotifyReceipt.ACCEPTED)
            
            # Verify logging was called
            mock_print.assert_called()


if __name__ == '__main__':
    unittest.main()