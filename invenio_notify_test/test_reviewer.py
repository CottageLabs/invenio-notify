from invenio_notify.records.models import ReviewerModel
from invenio_notify.services.config import ReviewerServiceConfig
from invenio_notify.services.service import ReviewerService
import pytest
from invenio_notify_test.reviewer_fixture import create_reviewer, reviewer_data, sample_reviewers


def create_reviewer_service():
    return ReviewerService(config=ReviewerServiceConfig)


def test_create_model(db, superuser_identity, reviewer_data):
    assert ReviewerModel.query.count() == 0
    reviewer_data = reviewer_data()

    # Create a new reviewer entry
    reviewer = ReviewerModel.create(reviewer_data)

    # Verify record was created
    assert ReviewerModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved = ReviewerModel.get(reviewer.id)
    assert retrieved.coar_id == reviewer_data['coar_id']
    assert retrieved.name == reviewer_data['name']
    assert retrieved.inbox_url == reviewer_data['inbox_url']
    assert retrieved.description == reviewer_data['description']


def test_service_create(test_app, superuser_identity, reviewer_data):
    reviewer_serv = create_reviewer_service()

    assert ReviewerModel.query.count() == 0
    reviewer_data = reviewer_data()

    result = reviewer_serv.create(superuser_identity, reviewer_data)

    result_dict = result.to_dict()
    assert result_dict['coar_id'] == reviewer_data['coar_id']
    assert result_dict['name'] == reviewer_data['name']
    assert result_dict['inbox_url'] == reviewer_data['inbox_url']
    assert result_dict['description'] == reviewer_data['description']
    assert 'links' in result_dict
    assert ReviewerModel.query.count() == 1


def test_service_search(test_app, superuser_identity, sample_reviewers):
    reviewer_serv = create_reviewer_service()

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

