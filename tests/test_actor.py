from invenio_accounts.testutils import create_test_user

from invenio_notify.proxies import current_actor_service
from invenio_notify.records.models import ActorModel
from tests.fixtures.actor_fixture import (
    create_actor,
    actor_data,
    sample_actors,
)
from tests.fixtures.user_fixture import create_test_users


def test_create_model(db, superuser_identity):
    assert ActorModel.query.count() == 0
    data = actor_data(inbox_api_token='test-api-token')

    # Create a new actor entry
    actor = ActorModel.create(data)

    # Verify record was created
    assert ActorModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved = ActorModel.get(actor.id)
    assert retrieved.actor_id == data['actor_id']
    assert retrieved.name == data['name']
    assert retrieved.inbox_url == data['inbox_url']
    assert retrieved.inbox_api_token == data['inbox_api_token']
    assert retrieved.description == data['description']


def test_service_create(test_app, superuser_identity):
    actor_serv = current_actor_service

    assert ActorModel.query.count() == 0
    data = actor_data()

    result = actor_serv.create(superuser_identity, data)

    result_dict = result.to_dict()
    assert result_dict['actor_id'] == data['actor_id']
    assert result_dict['name'] == data['name']
    assert result_dict['inbox_url'] == data['inbox_url']
    assert result_dict['inbox_api_token'] == data['inbox_api_token']
    assert result_dict['description'] == data['description']
    assert 'links' in result_dict
    assert ActorModel.query.count() == 1


def test_service_search(test_app, superuser_identity):
    actor_serv = current_actor_service

    assert ActorModel.query.count() == 0

    # Get sample actor data
    actors = sample_actors(3)
    actor_1, actor_2, actor_3 = actors

    # Create test records
    actor_serv.create(superuser_identity, actor_1)
    actor_serv.create(superuser_identity, actor_2)
    actor_serv.create(superuser_identity, actor_3)

    assert ActorModel.query.count() == 3

    # Search with filter by name
    result = actor_serv.search(superuser_identity, params={'q': '2'})
    result_list = result.to_dict()['hits']['hits']
    assert len(result_list) == 1
    assert result_list[0]['name'] == actor_2['name']

    # Verify all actors are in the unfiltered results
    result = actor_serv.search(superuser_identity)
    result_list = result.to_dict()['hits']['hits']
    actor_names = [item['name'] for item in result_list]
    assert actor_1['name'] in actor_names
    assert actor_2['name'] in actor_names
    assert actor_3['name'] in actor_names


def test_service_add_member(test_app, superuser_identity, db, create_actor):
    # Create actor service
    actor_serv = current_actor_service
    
    # Create a actor
    actor = create_actor()
    actor_id = actor.id
    
    # Create test users
    users = create_test_users()
    
    # Add members to the actor
    emails_to_add = [u.email for u in users[:2]]
    actor_serv.add_member(superuser_identity, actor_id, {"emails": emails_to_add})
    
    # Get the updated actor
    actor_model = ActorModel.get(actor_id)
    
    # Check if members were added correctly
    member_emails = [member.email for member in actor_model.members]
    assert "test1@example.com" in member_emails
    assert "test2@example.com" in member_emails
    assert "nonexistent@example.com" not in member_emails  # This email doesn't exist
    assert "test3@example.com" not in member_emails  # This email wasn't added
    
    # Try adding duplicate members (should be ignored)
    actor_serv.add_member(superuser_identity, actor_id, {"emails": ["test1@example.com", "test3@example.com"]})
    
    # Get the updated actor
    actor_model = ActorModel.get(actor_id)
    
    # Check that test3 was added but test1 wasn't duplicated
    member_emails = [member.email for member in actor_model.members]
    assert member_emails.count("test1@example.com") == 1  # Should only appear once
    assert "test3@example.com" in member_emails  # Should be added now


def test_service_del_member(test_app, superuser_identity, db, create_actor):
    # Create actor service
    actor_serv = current_actor_service
    
    # Create a actor
    actor = create_actor()
    actor_id = actor.id
    
    # Create test users
    users = create_test_users()
    
    # Add members to the actor
    emails_to_add = [u.email for u in users]
    actor_serv.add_member(superuser_identity, actor_id, {"emails": emails_to_add})
    
    # Get the updated actor
    actor_model = ActorModel.get(actor_id)
    
    # Verify all members were added
    member_emails = [member.email for member in actor_model.members]
    assert len(member_emails) == 3
    assert set(member_emails) == set(emails_to_add)
    
    # Remove the second user
    user_id_to_remove = users[1].id
    actor_serv.del_member(superuser_identity, actor_id, {"user_id": user_id_to_remove})
    
    # Get the updated actor
    actor_model = ActorModel.get(actor_id)
    
    # Check that the user was removed
    member_emails = [member.email for member in actor_model.members]
    assert len(member_emails) == 2
    assert "test2@example.com" not in member_emails
    assert "test1@example.com" in member_emails
    assert "test3@example.com" in member_emails
    
    # Try removing a user that is not a member (should not raise an error)
    non_member_user = create_test_user(email="nonmember@example.com")
    actor_serv.del_member(superuser_identity, actor_id, {"user_id": non_member_user.id})
    
    # Check that members remain unchanged
    actor_model = ActorModel.get(actor_id)
    member_emails = [member.email for member in actor_model.members]
    assert len(member_emails) == 2
    assert "test1@example.com" in member_emails
    assert "test3@example.com" in member_emails


def test_inbox_api_token_field(db, superuser_identity):
    """Test that inbox_api_token field works correctly."""
    
    # Test creating actor with inbox_api_token
    data_with_token = actor_data(
        actor_id='actor-with-token',
        inbox_api_token='secret-api-token-123'
    )
    
    actor_with_token = ActorModel.create(data_with_token)
    
    # Verify token was saved correctly
    assert actor_with_token.inbox_api_token == 'secret-api-token-123'
    
    # Test creating actor without inbox_api_token (should be None)
    data_without_token = actor_data(
        actor_id='actor-without-token',
        inbox_api_token=None
    )
    
    actor_without_token = ActorModel.create(data_without_token)
    
    # Verify token is None
    assert actor_without_token.inbox_api_token is None
    
    # Test service layer with inbox_api_token
    actor_serv = current_actor_service
    
    data_service_test = actor_data(
        actor_id='service-test-actor',
        inbox_api_token='service-token-456'
    )
    
    result = actor_serv.create(superuser_identity, data_service_test)
    result_dict = result.to_dict()
    
    # Verify token is included in service response
    assert result_dict['inbox_api_token'] == 'service-token-456'
