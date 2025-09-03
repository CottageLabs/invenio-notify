from invenio_notify.records.models import ActorMapModel
from invenio_notify.proxies import current_notify
from invenio_notify_test.fixtures.reviewer_map_fixture import create_reviewer_map_dict
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer


def test_create_model(db, superuser_identity, create_reviewer):
    assert ActorMapModel.query.count() == 0
    reviewer = create_reviewer()

    # Create a new reviewer map entry
    reviewer_map = ActorMapModel.create(
        create_reviewer_map_dict(reviewer.id, superuser_identity.id)
    )

    # Verify record was created
    assert ActorMapModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved_map = ActorMapModel.get(reviewer_map.id)
    assert retrieved_map.actor_id == reviewer.id
    assert retrieved_map.user_id == superuser_identity.id


def test_service_create(test_app, superuser_identity, create_reviewer):
    reviewer_map_serv = current_notify.reviewer_map_service

    assert ActorMapModel.query.count() == 0
    reviewer = create_reviewer()

    result = reviewer_map_serv.create(
        superuser_identity, 
        create_reviewer_map_dict(reviewer.id, superuser_identity.id)
    )

    result_dict = result.to_dict()
    assert result_dict['reviewer_id'] == reviewer.id
    assert result_dict['user_id'] == superuser_identity.id
    assert 'links' in result_dict
    assert ActorMapModel.query.count() == 1


def test_service_search(test_app, superuser_identity, create_reviewer):
    reviewer_map_serv = current_notify.reviewer_map_service

    assert ActorMapModel.query.count() == 0

    # Create multiple reviewer objects
    reviewer_1 = create_reviewer()
    reviewer_2 = create_reviewer()
    reviewer_3 = create_reviewer()

    # Create test records
    reviewer_map_serv.create(
        superuser_identity, 
        create_reviewer_map_dict(reviewer_1.id, superuser_identity.id)
    )
    reviewer_map_serv.create(
        superuser_identity, 
        create_reviewer_map_dict(reviewer_2.id, superuser_identity.id)
    )
    reviewer_map_serv.create(
        superuser_identity, 
        create_reviewer_map_dict(reviewer_3.id, superuser_identity.id)
    )

    assert ActorMapModel.query.count() == 3

    # Search with filter by reviewer_id
    result = reviewer_map_serv.search(superuser_identity, params={'q': reviewer_2.id})
    result_list = result.to_dict()['hits']['hits']
    assert len(result_list) == 1
    assert result_list[0]['reviewer_id'] == reviewer_2.id

    # Verify all reviewer_ids are in the unfiltered results
    result = reviewer_map_serv.search(superuser_identity)
    result_list = result.to_dict()['hits']['hits']
    reviewer_ids = [item['reviewer_id'] for item in result_list]
    assert reviewer_1.id in reviewer_ids
    assert reviewer_2.id in reviewer_ids
    assert reviewer_3.id in reviewer_ids

