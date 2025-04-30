from invenio_notify.records.models import ReviewerMapModel
from invenio_notify.services.config import ReviewerMapServiceConfig
from invenio_notify.services.service import ReviewerMapService


def create_reviewer_map_service():
    return ReviewerMapService(config=ReviewerMapServiceConfig)


def test_create_model(db, superuser_identity):
    assert ReviewerMapModel.query.count() == 0
    reviewer_id = 'external-reviewer-123'

    # Create a new reviewer map entry
    reviewer_map = ReviewerMapModel.create({
        'reviewer_id': reviewer_id,
        'user_id': superuser_identity.id
    })

    # Verify record was created
    assert ReviewerMapModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved_map = ReviewerMapModel.get(reviewer_map.id)
    assert retrieved_map.reviewer_id == reviewer_id
    assert retrieved_map.user_id == superuser_identity.id


def test_service_create(test_app, superuser_identity):
    reviewer_map_serv = create_reviewer_map_service()

    assert ReviewerMapModel.query.count() == 0
    reviewer_id = 'external-reviewer-123'

    result = reviewer_map_serv.create(superuser_identity, {
        'reviewer_id': reviewer_id,
        'user_id': superuser_identity.id
    })

    result_dict = result.to_dict()
    assert result_dict['reviewer_id'] == reviewer_id
    assert result_dict['user_id'] == superuser_identity.id
    assert 'links' in result_dict
    assert ReviewerMapModel.query.count() == 1


def test_service_search(test_app, superuser_identity):
    reviewer_map_serv = create_reviewer_map_service()

    assert ReviewerMapModel.query.count() == 0

    # Create multiple reviewer map entries
    reviewer_id_1 = 'external-reviewer-123'
    reviewer_id_2 = 'external-reviewer-456'
    reviewer_id_3 = 'external-reviewer-789'

    # Create test records
    reviewer_map_serv.create(superuser_identity, {
        'reviewer_id': reviewer_id_1,
        'user_id': superuser_identity.id
    })
    reviewer_map_serv.create(superuser_identity, {
        'reviewer_id': reviewer_id_2,
        'user_id': superuser_identity.id
    })
    reviewer_map_serv.create(superuser_identity, {
        'reviewer_id': reviewer_id_3,
        'user_id': superuser_identity.id
    })

    assert ReviewerMapModel.query.count() == 3

    # Search with filter by reviewer_id
    result = reviewer_map_serv.search(superuser_identity, params={'q': reviewer_id_2})
    result_list = result.to_dict()['hits']['hits']
    assert len(result_list) == 1
    assert result_list[0]['reviewer_id'] == reviewer_id_2

    # Verify all reviewer_ids are in the unfiltered results
    result = reviewer_map_serv.search(superuser_identity)
    result_list = result.to_dict()['hits']['hits']
    reviewer_ids = [item['reviewer_id'] for item in result_list]
    assert reviewer_id_1 in reviewer_ids
    assert reviewer_id_2 in reviewer_ids
    assert reviewer_id_3 in reviewer_ids
