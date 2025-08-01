from invenio_notify.proxies import current_inbox_service
from invenio_notify.records.models import NotifyInboxModel
from invenio_notify_test.fixtures.inbox_fixture import (
    create_inbox,
    create_inbox_payload__review,
)


def test_create_model(db, superuser_identity, create_inbox):
    assert NotifyInboxModel.query.count() == 0
    record_id = 'kajsdlkasjk'
    m = create_inbox(recid=record_id)
    m.commit()

    # find record by record_id
    new_m = NotifyInboxModel.search({'recid': record_id}, [])
    assert m == new_m[0]
    assert NotifyInboxModel.query.count() == 1


def test_service_create(test_app, superuser_identity):
    notify_inbox_serv = current_inbox_service

    assert NotifyInboxModel.query.count() == 0
    record_id = 'kajsdlkasjk'
    raw_payload = create_inbox_payload__review(record_id)
    result = notify_inbox_serv.create(superuser_identity, {
        'raw': raw_payload, 'recid': record_id
    })
    result_dict = result.to_dict()
    assert result_dict['recid'] == record_id
    # Extract UUID from raw_payload['id'] which has format 'urn:uuid:actual-uuid'
    expected_uuid = raw_payload['id'].replace('urn:uuid:', '')
    assert result_dict['noti_id'] == expected_uuid
    assert 'links' in result_dict
    assert NotifyInboxModel.query.count() == 1


def test_service_search(test_app, superuser_identity):
    notify_inbox_serv = current_inbox_service


    # Create multiple inbox records
    record_id_1 = 'record1'
    record_id_2 = 'record2'
    record_id_3 = 'record3'

    # Create test records
    notify_inbox_serv.create(superuser_identity, {
        'raw': create_inbox_payload__review(record_id_1), 'recid': record_id_1,
    })
    notify_inbox_serv.create(superuser_identity, {
        'raw': create_inbox_payload__review(record_id_2), 'recid': record_id_2,
    })
    notify_inbox_serv.create(superuser_identity, {
        'raw': create_inbox_payload__review(record_id_3), 'recid': record_id_3,
    })

    assert NotifyInboxModel.query.count() == 3

    # Search without parameters should return all records
    result = notify_inbox_serv.search(superuser_identity)
    result_list = result.to_dict()['hits']['hits']
    assert len(result_list) == 3

    # Verify record_ids are in the results
    record_ids = [item['recid'] for item in result_list]
    assert record_id_1 in record_ids
    assert record_id_2 in record_ids
    assert record_id_3 in record_ids
