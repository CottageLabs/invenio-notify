from invenio_oauth2server.models import Token

from invenio_notify.records.models import ReviewerMapModel
from invenio_notify.scopes import inbox_scope
from invenio_notify.utils import user_utils
from invenio_notify_test.fixtures import inbox_fixture
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer


def create_scope_token(user):
    token = Token.create_personal('token-name-1', user.id, scopes=[inbox_scope.id])
    return token


def create_reviewer_map(db, user_id, reviewer_id):
    """Create a reviewer map entry and commit to the database."""
    ReviewerMapModel.create({
        'user_id': user_id,
        'reviewer_id': reviewer_id,
    })
    db.session.commit()


def send_inbox(client, token, notify_review_data):
    """Make an authenticated request to the inbox endpoint."""
    headers = {'Authorization': f'Bearer {token.access_token}'}
    return client.post("/api/notify/inbox", json=notify_review_data, headers=headers)


def create_notify_user(db, superuser_identity):
    user = superuser_identity.user
    user_utils.add_coarnotify_action(db, user.id)
    token = create_scope_token(user)
    return token, user


def setup_user_reviewer_with_actor_id(db, superuser_identity, actor_id, create_reviewer):
    """Setup user, token, and reviewer with specified actor_id."""
    token, user = create_notify_user(db, superuser_identity)
    reviewer = create_reviewer(actor_id=actor_id)
    create_reviewer_map(db, user.id, reviewer.id)
    return token, user, reviewer


def test_inbox_401(client):
    notify_review_data = inbox_fixture.create_notification_data('test-record-id')
    response = client.post("/api/notify/inbox", json=notify_review_data)
    assert response.status_code == 401


def test_inbox__success(client, db, superuser_identity, rdm_record, create_reviewer):
    # logging.basicConfig(
    #     level=logging.DEBUG,  # Capture all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    # )
    # logging.getLogger("invenio_notify").setLevel(logging.DEBUG)

    notify_review_data = inbox_fixture.create_notification_data(rdm_record.id)
    token, user, reviewer = setup_user_reviewer_with_actor_id(
        db, superuser_identity, notify_review_data['actor']['id'], create_reviewer
    )

    response = send_inbox(client, token, notify_review_data)
    assert response.status_code == 202
    assert response.json['message'] == 'Accepted'


def test_inbox__actor_id_mismatch(client, db, superuser_identity, rdm_record, create_reviewer):
    notify_review_data = inbox_fixture.create_notification_data(rdm_record.id)
    
    # Create a reviewer with a different ID to cause a mismatch
    token, user, reviewer = setup_user_reviewer_with_actor_id(
        db, superuser_identity, notify_review_data['actor']['id'] + 'wrong', create_reviewer
    )

    response = send_inbox(client, token, notify_review_data)
    assert response.status_code == 403
    assert response.json['message'] == 'Actor Id mismatch'

