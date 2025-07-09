import pytest
from invenio_oauth2server.models import Token

from invenio_notify.records.models import ReviewerMapModel
from invenio_notify.scopes import inbox_scope
from invenio_notify.utils import user_utils
from invenio_notify_test.fixtures.inbox_payload import payload_review
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


@pytest.fixture
def user_reviewer_setup(db, superuser_identity, create_reviewer):
    """Fixture to setup user, token, and reviewer with specified actor_id."""
    
    def _setup(actor_id):
        """Setup user, token, and reviewer with specified actor_id.
        
        Args:
            actor_id: Actor ID for the reviewer
            
        Returns:
            tuple: (token, user, reviewer)
        """
        token, user = create_notify_user(db, superuser_identity)
        reviewer = create_reviewer(actor_id=actor_id)
        create_reviewer_map(db, user.id, reviewer.id)
        return token, user, reviewer
    
    return _setup


def test_inbox_401(client):
    notify_review_data = payload_review('test-record-id')
    response = client.post("/api/notify/inbox", json=notify_review_data)
    assert response.status_code == 401


def test_inbox__success(client, rdm_record, user_reviewer_setup):
    notify_review_data = payload_review(rdm_record.id)
    token, user, reviewer = user_reviewer_setup(notify_review_data['actor']['id'])

    response = send_inbox(client, token, notify_review_data)
    assert response.status_code == 202
    assert response.json['message'] == 'Accepted'


def test_inbox__actor_id_mismatch(client, rdm_record, user_reviewer_setup):
    notify_review_data = payload_review(rdm_record.id)
    token, user, reviewer = user_reviewer_setup(notify_review_data['actor']['id'] + 'wrong')

    response = send_inbox(client, token, notify_review_data)
    assert response.status_code == 403
    assert response.json['message'] == 'Actor Id mismatch'



def test_inbox__duplicate_noti_id(client, rdm_record, user_reviewer_setup):
    notify_review_data = payload_review(rdm_record.id)
    token, user, reviewer = user_reviewer_setup(notify_review_data['actor']['id'])

    # Send the same notification first time - should succeed
    response1 = send_inbox(client, token, notify_review_data)
    assert response1.status_code == 202
    assert response1.json['message'] == 'Accepted'

    # Send the same notification second time - should fail due to duplicate noti_id
    response2 = send_inbox(client, token, notify_review_data)
    assert response2.status_code == 400
    assert response2.json['message'] == 'Failed to create inbox record'