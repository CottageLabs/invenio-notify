from invenio_notify.records.models import ActorMapModel
from invenio_notify.proxies import current_notify
from tests.fixtures.actor_map_fixture import create_actor_map_dict
from tests.fixtures.actor_fixture import create_actor


def test_create_model(db, superuser_identity, create_actor):
    assert ActorMapModel.query.count() == 0
    actor = create_actor()

    # Create a new actor map entry
    actor_map = ActorMapModel.create(
        create_actor_map_dict(actor.id, superuser_identity.id)
    )

    # Verify record was created
    assert ActorMapModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved_map = ActorMapModel.get(actor_map.id)
    assert retrieved_map.actor_id == actor.id
    assert retrieved_map.user_id == superuser_identity.id


def test_service_create(test_app, superuser_identity, create_actor):
    actor_map_serv = current_notify.actor_map_service

    assert ActorMapModel.query.count() == 0
    actor = create_actor()

    result = actor_map_serv.create(
        superuser_identity, 
        create_actor_map_dict(actor.id, superuser_identity.id)
    )

    result_dict = result.to_dict()
    assert result_dict['actor_id'] == actor.id
    assert result_dict['user_id'] == superuser_identity.id
    assert 'links' in result_dict
    assert ActorMapModel.query.count() == 1


def test_service_search(test_app, superuser_identity, create_actor):
    actor_map_serv = current_notify.actor_map_service

    assert ActorMapModel.query.count() == 0

    # Create multiple actor objects
    actor_1 = create_actor()
    actor_2 = create_actor()
    actor_3 = create_actor()

    # Create test records
    actor_map_serv.create(
        superuser_identity, 
        create_actor_map_dict(actor_1.id, superuser_identity.id)
    )
    actor_map_serv.create(
        superuser_identity, 
        create_actor_map_dict(actor_2.id, superuser_identity.id)
    )
    actor_map_serv.create(
        superuser_identity, 
        create_actor_map_dict(actor_3.id, superuser_identity.id)
    )

    assert ActorMapModel.query.count() == 3

    # Search with filter by actor_id
    result = actor_map_serv.search(superuser_identity, params={'q': actor_2.id})
    result_list = result.to_dict()['hits']['hits']
    assert len(result_list) == 1
    assert result_list[0]['actor_id'] == actor_2.id

    # Verify all actor_ids are in the unfiltered results
    result = actor_map_serv.search(superuser_identity)
    result_list = result.to_dict()['hits']['hits']
    actor_ids = [item['actor_id'] for item in result_list]
    assert actor_1.id in actor_ids
    assert actor_2.id in actor_ids
    assert actor_3.id in actor_ids

