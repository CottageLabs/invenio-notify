import json
from pathlib import Path

from flask import Flask, request

from coarnotify.exceptions import NotifyException
from coarnotify.server import COARNotifyReceipt, COARNotifyServer, COARNotifyServiceBinding
from invenio_notify.utils.notify_response import create_fail_response, response_coar_notify_receipt

app = Flask(__name__)


class DummyPCIHandler:
    def __init__(self):
        self.path = Path.home() / '.local/opt/dummy_pci_handler/store.json'




class DummyCOARNotifyReceipt:
    """Dummy version of COARNotifyReceipt for testing."""
    ACCEPTED = COARNotifyReceipt.ACCEPTED
    CREATED = COARNotifyReceipt.CREATED

    def __init__(self, status, location=None):
        self.status = status
        self.location = location


class DummyInboxCOARBinding(COARNotifyServiceBinding):
    """Dummy version of InboxCOARBinding for testing."""

    def notification_received(self, notification):
        """Process a notification and return a receipt."""
        print(f"Dummy binding received notification: {notification}")

        # Convert to dict for logging if it's a NotifyPattern object
        if hasattr(notification, 'to_jsonld'):
            notification_data = notification.to_jsonld()
        else:
            notification_data = notification

        # Log the notification for debugging
        if isinstance(notification_data, dict):
            print(f"Notification ID: {notification_data.get('id', 'N/A')}")
            print(f"Notification type: {notification_data.get('type', 'N/A')}")
            print(f"Actor ID: {notification_data.get('actor', {}).get('id', 'N/A')}")

        # Always return accepted for dummy implementation
        return COARNotifyReceipt(COARNotifyReceipt.ACCEPTED)


@app.route('/dummy-reviewer/dummy-inbox', methods=['POST'])
def dummy_inbox():
    """Dummy reviewer inbox endpoint for testing purposes."""

    # Handle POST requests like InboxApiResource.receive_notification
    try:
        # Check if request has JSON data
        if not request.is_json:
            return create_fail_response(400, "Request must be JSON")

        data = request.get_json()
        if not data:
            return create_fail_response(400, "Request must be JSON")

        print(f"Received notification data: {data}")

        # Process notification using COARNotifyServer with dummy binding
        server = COARNotifyServer(DummyInboxCOARBinding())
        receipt = server.receive(data, validate=True)

        # Return response in COAR notify receipt format
        return response_coar_notify_receipt(receipt)

    except json.JSONDecodeError:
        return create_fail_response(400, "Invalid JSON format")

    except NotifyException:
        return create_fail_response(400, "Notification processing failed")


    except Exception as e:
        print(f"Error processing notification: {e}")
        return create_fail_response(500, "Error processing notification")


def run():
    """Run the dummy reviewer Flask server."""
    try:
        print("Starting dummy reviewer server...")
        print("Server will be available at: http://localhost:5000/dummy-reviewer/dummy-inbox")
        app.run(debug=True, host='0.0.0.0', port=53010)
    except Exception as e:
        print(f"Error starting server: {e}")
        raise


if __name__ == '__main__':
    run()
