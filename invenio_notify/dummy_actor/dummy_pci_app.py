import json
from pathlib import Path

import requests
from flask import Flask, request
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from coarnotify.exceptions import NotifyException
from coarnotify.server import COARNotifyReceipt, COARNotifyServer, COARNotifyServiceBinding
from invenio_notify.utils.notify_response import response_coar_notify_receipt, \
    create_default_msg_by_status
from invenio_notify_test.fixtures.inbox_payload import payload_endorsement_resp, payload_review, \
    payload_tentative_accept, payload_reject, payload_tentative_reject

app = Flask(__name__)
console = Console()

def create_fail_response(status, msg=None):
    msg = msg or create_default_msg_by_status(status)
    return {"status": status, "message": msg}, status

def print_json_panel(data, title, border_style="blue"):
    """Print JSON data in a formatted panel with syntax highlighting."""
    json_str = json.dumps(data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style=border_style))


class DummyPCIBackend:
    def __init__(self):
        self.store_path = Path.home() / '.local/opt/dummy_pci_handler/store.json'
        self.reply_inbox_url = 'https://127.0.0.1:5000/api/notify/inbox'

    def load_notifications(self) -> list:
        """Load notifications from JSON file."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

        notifications = []
        if self.store_path.exists():
            try:
                with open(self.store_path, 'r') as f:
                    notifications = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                notifications = []

        return notifications

    def save_notifications(self, notifications: list):
        """Save notifications list to JSON file."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.store_path, 'w') as f:
            json.dump(notifications, f, indent=2)

    def save(self, noti: dict):
        """Save notification to JSON file."""
        notifications = self.load_notifications()
        notifications.append(noti)
        self.save_notifications(notifications)

    def print_notifications(self):
        """Print all notifications in store."""
        notifications = self.load_notifications()
        
        if not notifications:
            print("No notifications in store")
            return
        
        print(f"Found {len(notifications)} notification(s) in store:")
        print("=" * 60)
        
        for i, notification in enumerate(notifications, 1):
            print(f"Notification {i}:")
            print(f"  ID: {notification.get('id', 'N/A')}")
            print(f"  Type: {notification.get('type', 'N/A')}")
            print(f"  Actor: {notification.get('actor', {}).get('name', 'N/A')}")
            print(f"  Context: {notification.get('context', {}).get('id', 'N/A')}")
            print(f"  Object: {notification.get('object', {}).get('id', 'N/A')}")
            print("-" * 40)

    def reply_last(self, token, payload_type='endorsement'):
        """Reply to the last notification in store and remove it."""
        notifications = self.load_notifications()

        if not notifications:
            console.print("[red]No notifications in store to reply to[/red]")
            return

        last_notification = notifications[-1]
        notification_id = last_notification.get('id', 'N/A')
        
        console.print(Panel(
            f"[bold blue]Replying to notification:[/bold blue] {notification_id}",
            title="Reply Operation",
            border_style="blue"
        ))

        # Extract record_id from context if available
        context = last_notification.get('object', {})
        context_id = context.get('id', '')
        record_id = context_id.split('/')[-1] if context_id else '1'

        # Get the notification ID to reply to
        in_reply_to = last_notification.get('id', '')

        # Create payload based on type
        payload_functions = {
            'endorsement': payload_endorsement_resp,
            'review': payload_review,
            'tentative_accept': payload_tentative_accept,
            'tentative_reject': payload_tentative_reject,
            'reject': payload_reject
        }

        if payload_type not in payload_functions:
            console.print(f"[red]Unknown payload type: {payload_type}[/red]")
            return

        payload = payload_functions[payload_type](record_id, in_reply_to)
        payload['actor']['id'] = last_notification['target']['id']

        # Display source notification with rich formatting
        console.print("\n[bold cyan]Source notification:[/bold cyan]")
        print_json_panel(last_notification, "Source Notification", "cyan")

        # Display generated payload with rich formatting
        console.print("\n[bold green]Generated payload:[/bold green]")
        print_json_panel(payload, "Generated Payload", "green")

        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        try:
            # Send POST request to reply_inbox_url
            response = requests.post(
                self.reply_inbox_url,
                json=payload,
                headers=headers,
                verify=False,
            )

            # Create status color based on response code
            if response.status_code in [200, 201, 202]:
                status_color = "green"
                status_text = "✓ SUCCESS"
            else:
                status_color = "red"
                status_text = "✗ FAILED"

            console.print(f"\n[{status_color}]{status_text}[/{status_color}] Response status: {response.status_code}")

            # Print response JSON if available
            try:
                response_json = response.json()
                print_json_panel(response_json, "Response JSON", status_color)
            except ValueError:
                console.print(Panel(response.text, title="Response Text", border_style=status_color))

        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error sending request: {e}[/red]")
            return
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            return

        # Remove last notification from store if request was successful
        if response.status_code not in [200, 201, 202]:
            console.print(f"[yellow]Request failed status[{response.status_code}], notification will be kept in store[/yellow]")

        if payload_type not in ['tentative_accept', 'review']:
            notifications.pop()  # Remove last notification
            self.save_notifications(notifications)
            console.print("[green]Last notification removed from store[/green]")



    def reset(self):
        """Reset the store to empty list."""
        self.save_notifications([])


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


@app.route('/dummy-actor/dummy-inbox', methods=['POST'])
def dummy_inbox():
    """Dummy actor inbox endpoint for testing purposes."""
    print("Received request at /dummy-actor/dummy-inbox")

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return create_fail_response(401, "Unauthorized: Missing or invalid token")

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

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return create_fail_response(400, "Invalid JSON format")

    except NotifyException as e:
        print(f"Notification processing failed: {e}")
        return create_fail_response(400, f"Notification processing failed: {e}")


    except Exception as e:
        print(f"Error processing notification: {e}")
        return create_fail_response(500, "Error processing notification")


def run():
    """Run the dummy actor Flask server."""
    port = 53010
    try:
        print("Starting dummy actor server...")
        print(f"Server will be available at: http://localhost:{port}/dummy-actor/dummy-inbox")
        app.run(debug=True, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Error starting server: {e}")
        raise


if __name__ == '__main__':
    run()
