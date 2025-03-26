from invenio_oauth2server.models import Token

from invenio_notify.utils import user_utils
from invenio_notify_test import inbox_fixture


def test_inbox_401(client):
    notify_review_data = inbox_fixture.create_notification_data('test-record-id')
    response = client.post("/api/notify-rest/inbox", json=notify_review_data)
    assert response.status_code == 401


def test_inbox__success(client, db, superuser_identity, rdm_record):
    # logging.basicConfig(
    #     level=logging.DEBUG,  # Capture all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    # )
    # logging.getLogger("invenio_notify").setLevel(logging.DEBUG)

    user = superuser_identity.user

    user_utils.add_user_action(db, user.id)

    token = Token.create_personal('token-name-1', user.id, scopes=['notify:inbox'])
    access_token = token.access_token

    notify_review_data = inbox_fixture.create_notification_data(rdm_record.id)

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post("/api/notify-rest/inbox", json=notify_review_data, headers=headers)
    assert response.status_code == 202
