import pytest
from datetime import datetime, timedelta
from invenio_oauth2server.models import Token, Client

from invenio_notify.utils import user_utils
from invenio_notify_test import inbox_fixture


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


def _generate_pat_token(
        db,
        uploader,
        client,
        access_token,
        scope,
        expires=datetime.utcnow() + timedelta(hours=10),
):
    """Create a personal access token."""
    """
    from invenio-rdm-records test_resources_access
    """
    with db.session.begin_nested():
        token_ = Token(
            client_id=client,
            user_id=uploader.id,
            access_token=access_token,
            expires=expires,
            is_personal=False,
            is_internal=True,
        )
        db.session.add(token_)
    db.session.commit()

    token_.scopes = [scope]
    return dict(
        token=token_,
        auth_header=[
            ("Authorization", "Bearer {0}".format(token_.access_token)),
        ],
    )


def create_oauth2_client(db, user):
    """Create client."""
    with db.session.begin_nested():
        # create resource_owner -> client_1
        client_ = Client(
            client_id="client_test_u1c1",
            client_secret="client_test_u1c1",
            name="client_test_u1c1",
            description="",
            is_confidential=False,
            user_id=user.id,
            _redirect_uris="",
            _default_scopes="",
        )
        db.session.add(client_)
    db.session.commit()
    return client_.client_id


def test_inbox__success(client, db, superuser_identity, rdm_record):
    # logging.basicConfig(
    #     level=logging.DEBUG,  # Capture all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    # )
    # logging.getLogger("invenio_notify").setLevel(logging.DEBUG)

    user = superuser_identity.user

    user_utils.add_user_action(db, user.id)

    client_id = create_oauth2_client(db, user)

    # user_token = Token.create(
    #     user_id=user.id,
    #     client_id=None,  # None for personal access tokens
    #     token_type='bearer',
    #     access_token="notify:inbox",
    #     refresh_token=None,
    #     expires=datetime.now() + timedelta(days=1),
    #     is_internal=True,
    #     scopes=['read', 'write']
    # )
    # db.session.add(user_token)
    # db.session.commit()

    access_token = 'xxx'
    _generate_pat_token(db,
                        user,
                        client_id,
                        access_token=access_token,
                        scope="notify:inbox",
                        )

    notify_review_data = inbox_fixture.create_notification_data(rdm_record.id)

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post("/api/notify-rest/inbox", json=notify_review_data, headers=headers)
    assert response.status_code == 202
