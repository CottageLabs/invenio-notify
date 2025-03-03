import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from invenio_app.factory import create_app


# @pytest.fixture
# def client():
#     app = create_app("TEST")
#     return app.test_client()
#
#
# def record_id():
#     return "12345"
#
#
# def valid_payload():
#     return {"key": "value"}
#
#
# def invalid_payload():
#     return "invalid json"
#
#
# @patch("path.to.COARNotifyServer.receive")
# def test_inbox_success(mock_receive, client, record_id, valid_payload):
#     """Test successful processing of inbox request."""
#     mock_response = MagicMock()
#     mock_response.location = "/some/location"
#     mock_response.status = 200
#     mock_receive.return_value = mock_response
#
#     response = client.post(f"/inbox/{record_id}",
#                            data=json.dumps(valid_payload),
#                            content_type='application/json')
#
#     assert response.status_code == 200
#     assert "inbox Done" in response.json["message"]
#
#
# def test_inbox_invalid_json(client, record_id, invalid_payload):
#     """Test request with invalid JSON payload."""
#     response = client.post(f"/inbox/{record_id}",
#                            data=invalid_payload,
#                            content_type='application/json')
#
#     assert response.status_code == 400
#     assert "Request must be JSON" in response.json["error"]
#
#
# @patch("path.to.COARNotifyServer.receive", side_effect=Exception("Processing error"))
# def test_inbox_server_error(mock_receive, client, record_id, valid_payload):
#     """Test handling of server error."""
#     response = client.post(f"/inbox/{record_id}",
#                            data=json.dumps(valid_payload),
#                            content_type='application/json')
#
#     assert response.status_code == 500
#     assert "Processing error" in response.json["error"]


@pytest.fixture
def notify_review_data_1():
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams"
        ],
        "id": "urn:uuid:62b968af854542968b5752f94dba843b",
        "type": [
            "Announce",
            "coar-notify:ReviewAction"
        ],
        "actor": {
            "id": "https://cottagelabs.com/",
            "type": "Service",
            "name": "My Review Service"
        },
        "object": {
            "id": "urn:uuid:a1d039c8b51f4d6a8f22df23dea58541",
            "type": "Document",
            "ietf:cite-as": "https://dx.doi.org/10.12345/6789"
        },
        "origin": {
            "id": "https://cottagelabs.com/",
            "type": "Service",
            "inbox": "https://cottagelabs.com/inbox"
        },
        "target": {
            "id": "https://example.com/",
            "type": "Service",
            "inbox": "http://localhost:5005/inbox"
        }
    }


def test_inbox_401(client, notify_review_data_1):
    response = client.post("/api/notify-rest/inbox/aaa", json=notify_review_data_1)
    assert response.status_code == 401