from invenio_accounts.testutils import create_test_user

from invenio_notify.proxies import current_reviewer_service
from invenio_notify.records.models import ReviewerModel
from invenio_notify_test.fixtures.reviewer_fixture import (
    create_reviewer,
    reviewer_data,
    sample_reviewers,
)
from invenio_notify_test.fixtures.user_fixture import create_test_users


def test_create_model(db, superuser_identity):
    assert ReviewerModel.query.count() == 0
    data = reviewer_data(inbox_api_token='test-api-token')

    # Create a new reviewer entry
    reviewer = ReviewerModel.create(data)

    # Verify record was created
    assert ReviewerModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved = ReviewerModel.get(reviewer.id)
    assert retrieved.actor_id == data['actor_id']
    assert retrieved.name == data['name']
    assert retrieved.inbox_url == data['inbox_url']
    assert retrieved.inbox_api_token == data['inbox_api_token']
    assert retrieved.description == data['description']


def test_service_create(test_app, superuser_identity):
    reviewer_serv = current_reviewer_service

    assert ReviewerModel.query.count() == 0
    data = reviewer_data()

    result = reviewer_serv.create(superuser_identity, data)

    result_dict = result.to_dict()
    assert result_dict['actor_id'] == data['actor_id']
    assert result_dict['name'] == data['name']
    assert result_dict['inbox_url'] == data['inbox_url']
    assert result_dict['inbox_api_token'] == data['inbox_api_token']
    assert result_dict['description'] == data['description']
    assert 'links' in result_dict
    assert ReviewerModel.query.count() == 1


def test_service_search(test_app, superuser_identity):
    reviewer_serv = current_reviewer_service

    assert ReviewerModel.query.count() == 0

    # Get sample reviewer data
    reviewers = sample_reviewers(3)
    reviewer_1, reviewer_2, reviewer_3 = reviewers

    # Create test records
    reviewer_serv.create(superuser_identity, reviewer_1)
    reviewer_serv.create(superuser_identity, reviewer_2)
    reviewer_serv.create(superuser_identity, reviewer_3)

    assert ReviewerModel.query.count() == 3

    # Search with filter by name
    result = reviewer_serv.search(superuser_identity, params={'q': '2'})
    result_list = result.to_dict()['hits']['hits']
    assert len(result_list) == 1
    assert result_list[0]['name'] == reviewer_2['name']

    # Verify all reviewers are in the unfiltered results
    result = reviewer_serv.search(superuser_identity)
    result_list = result.to_dict()['hits']['hits']
    reviewer_names = [item['name'] for item in result_list]
    assert reviewer_1['name'] in reviewer_names
    assert reviewer_2['name'] in reviewer_names
    assert reviewer_3['name'] in reviewer_names


def test_service_add_member(test_app, superuser_identity, db, create_reviewer):
    # Create reviewer service
    reviewer_serv = current_reviewer_service
    
    # Create a reviewer
    reviewer = create_reviewer()
    reviewer_id = reviewer.id
    
    # Create test users
    users = create_test_users()
    
    # Add members to the reviewer
    emails_to_add = [u.email for u in users[:2]]
    reviewer_serv.add_member(superuser_identity, reviewer_id, {"emails": emails_to_add})
    
    # Get the updated reviewer
    reviewer_model = ReviewerModel.get(reviewer_id)
    
    # Check if members were added correctly
    member_emails = [member.email for member in reviewer_model.members]
    assert "test1@example.com" in member_emails
    assert "test2@example.com" in member_emails
    assert "nonexistent@example.com" not in member_emails  # This email doesn't exist
    assert "test3@example.com" not in member_emails  # This email wasn't added
    
    # Try adding duplicate members (should be ignored)
    reviewer_serv.add_member(superuser_identity, reviewer_id, {"emails": ["test1@example.com", "test3@example.com"]})
    
    # Get the updated reviewer
    reviewer_model = ReviewerModel.get(reviewer_id)
    
    # Check that test3 was added but test1 wasn't duplicated
    member_emails = [member.email for member in reviewer_model.members]
    assert member_emails.count("test1@example.com") == 1  # Should only appear once
    assert "test3@example.com" in member_emails  # Should be added now


def test_service_del_member(test_app, superuser_identity, db, create_reviewer):
    # Create reviewer service
    reviewer_serv = current_reviewer_service
    
    # Create a reviewer
    reviewer = create_reviewer()
    reviewer_id = reviewer.id
    
    # Create test users
    users = create_test_users()
    
    # Add members to the reviewer
    emails_to_add = [u.email for u in users]
    reviewer_serv.add_member(superuser_identity, reviewer_id, {"emails": emails_to_add})
    
    # Get the updated reviewer
    reviewer_model = ReviewerModel.get(reviewer_id)
    
    # Verify all members were added
    member_emails = [member.email for member in reviewer_model.members]
    assert len(member_emails) == 3
    assert set(member_emails) == set(emails_to_add)
    
    # Remove the second user
    user_id_to_remove = users[1].id
    reviewer_serv.del_member(superuser_identity, reviewer_id, {"user_id": user_id_to_remove})
    
    # Get the updated reviewer
    reviewer_model = ReviewerModel.get(reviewer_id)
    
    # Check that the user was removed
    member_emails = [member.email for member in reviewer_model.members]
    assert len(member_emails) == 2
    assert "test2@example.com" not in member_emails
    assert "test1@example.com" in member_emails
    assert "test3@example.com" in member_emails
    
    # Try removing a user that is not a member (should not raise an error)
    non_member_user = create_test_user(email="nonmember@example.com")
    reviewer_serv.del_member(superuser_identity, reviewer_id, {"user_id": non_member_user.id})
    
    # Check that members remain unchanged
    reviewer_model = ReviewerModel.get(reviewer_id)
    member_emails = [member.email for member in reviewer_model.members]
    assert len(member_emails) == 2
    assert "test1@example.com" in member_emails
    assert "test3@example.com" in member_emails


def test_inbox_api_token_field(db, superuser_identity):
    """Test that inbox_api_token field works correctly."""
    
    # Test creating reviewer with inbox_api_token
    data_with_token = reviewer_data(
        actor_id='reviewer-with-token',
        inbox_api_token='secret-api-token-123'
    )
    
    reviewer_with_token = ReviewerModel.create(data_with_token)
    
    # Verify token was saved correctly
    assert reviewer_with_token.inbox_api_token == 'secret-api-token-123'
    
    # Test creating reviewer without inbox_api_token (should be None)
    data_without_token = reviewer_data(
        actor_id='reviewer-without-token',
        inbox_api_token=None
    )
    
    reviewer_without_token = ReviewerModel.create(data_without_token)
    
    # Verify token is None
    assert reviewer_without_token.inbox_api_token is None
    
    # Test service layer with inbox_api_token
    reviewer_serv = current_reviewer_service
    
    data_service_test = reviewer_data(
        actor_id='service-test-reviewer',
        inbox_api_token='service-token-456'
    )
    
    result = reviewer_serv.create(superuser_identity, data_service_test)
    result_dict = result.to_dict()
    
    # Verify token is included in service response
    assert result_dict['inbox_api_token'] == 'service-token-456'
