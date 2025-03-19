import pytest


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
    response = client.post("/api/notify-rest/inbox", json=notify_review_data_1)
    assert response.status_code == 401
