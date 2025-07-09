import json
from pathlib import Path

import requests
from flask import Flask, request

from coarnotify.exceptions import NotifyException
from coarnotify.server import COARNotifyReceipt, COARNotifyServer, COARNotifyServiceBinding
from invenio_notify.utils.notify_response import create_fail_response, response_coar_notify_receipt
from invenio_notify_test.fixtures.inbox_payload import payload_endorsement_resp, payload_review, \
    payload_tentative_accept, payload_reject

app = Flask(__name__)


class DummyPCIBackend:
    def __init__(self):
        self.path = Path.home() / '.local/opt/dummy_pci_handler/store.json'
        self.reply_inbox_url = 'https://127.0.0.1:5000/api/notify/inbox'

    def load_notifications(self) -> list:
        """Load notifications from JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        notifications = []
        if self.path.exists():
            try:
                with open(self.path, 'r') as f:
                    notifications = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                notifications = []

        return notifications

    def save_notifications(self, notifications: list):
        """Save notifications list to JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(notifications, f, indent=2)

    def save(self, noti: dict):
        """Save notification to JSON file."""
        notifications = self.load_notifications()
        notifications.append(noti)
        self.save_notifications(notifications)

    def reply_last(self, payload_type='endorsement_resp'):
        """Reply to the last notification in store and remove it."""
        notifications = self.load_notifications()

        if not notifications:
            print("No notifications in store to reply to")
            return

        last_notification = notifications[-1]
        print(f"Replying to notification: {last_notification.get('id', 'N/A')}")

        # Extract record_id from context if available
        context = last_notification.get('context', {})
        context_id = context.get('id', '')
        record_id = context_id.split('/')[-1] if context_id else '1'

        # Get the notification ID to reply to
        in_reply_to = last_notification.get('id', '').replace('urn:uuid:', '')

        # Create payload based on type
        payload_functions = {
            'endorsement_resp': payload_endorsement_resp,
            'review': payload_review,
            'tentative_accept': payload_tentative_accept,
            'reject': payload_reject
        }

        if payload_type not in payload_functions:
            print(f"Unknown payload type: {payload_type}")
            return

        payload = payload_functions[payload_type](record_id, in_reply_to)

        try:
            # Send POST request to reply_inbox_url
            response = requests.post(
                self.reply_inbox_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            print(f"Response status: {response.status_code}")

            # Print response JSON if available
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except ValueError:
                print(f"Response text: {response.text}")

            # Remove last notification from store if request was successful
            if response.status_code in [200, 201, 202]:
                notifications.pop()  # Remove last notification
                self.save_notifications(notifications)
                print("Last notification removed from store")
            else:
                print("Request failed, notification not removed from store")

        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


class DummyCOARNotifyReceipt:
    """Dummy version of COARNotifyReceipt for testing."""
    ACCEPTED = COARNotifyReceipt.ACCEPTED
    CREATED = COARNotifyReceipt.CREATED

    def __init__(self, status, location=None):
        self.status = status
        self.location = location


class DummyInboxCOARBinding(COARNotifyServiceBinding):
    """Dummy version of InboxCOARBinding for testing."""

    def __init__(self):
        self.handler = DummyPCIBackend()

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

        # Save notification using DummyPCIHandler
        self.handler.save(notification_data)

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
