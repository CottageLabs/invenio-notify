from invenio_notify.records.models import ReviewerModel
from invenio_notify.services.config import ReviewerServiceConfig
from invenio_notify.services.service import ReviewerService
import pytest
from invenio_notify_test.reviewer_fixture import create_reviewer, create_reviewer_service, reviewer_data, sample_reviewers




def test_create_model(db, superuser_identity):
    assert ReviewerModel.query.count() == 0
    data = reviewer_data()

    # Create a new reviewer entry
    reviewer = ReviewerModel.create(data)

    # Verify record was created
    assert ReviewerModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved = ReviewerModel.get(reviewer.id)
    assert retrieved.coar_id == data['coar_id']
    assert retrieved.name == data['name']
    assert retrieved.inbox_url == data['inbox_url']
    assert retrieved.description == data['description']


def test_service_create(test_app, superuser_identity):
    reviewer_serv = create_reviewer_service()

    assert ReviewerModel.query.count() == 0
    data = reviewer_data()

    result = reviewer_serv.create(superuser_identity, data)

    result_dict = result.to_dict()
    assert result_dict['coar_id'] == data['coar_id']
    assert result_dict['name'] == data['name']
    assert result_dict['inbox_url'] == data['inbox_url']
    assert result_dict['description'] == data['description']
    assert 'links' in result_dict
    assert ReviewerModel.query.count() == 1


def test_service_search(test_app, superuser_identity):
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
