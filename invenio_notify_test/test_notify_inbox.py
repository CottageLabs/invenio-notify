from invenio_notify.records.models import NotifyInboxModel
from invenio_notify.services.config import NotifyInboxServiceConfig
from invenio_notify.services.service import NotifyInboxService
from invenio_notify_test.fixtures.inbox_fixture import create_inbox, create_notification_data


def create_notify_inbox_service():
    return NotifyInboxService(config=NotifyInboxServiceConfig)


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
    notify_inbox_serv = create_notify_inbox_service()

    assert NotifyInboxModel.query.count() == 0
    record_id = 'kajsdlkasjk'
    result = notify_inbox_serv.create(superuser_identity, {
        'raw': create_notification_data(record_id), 'recid': record_id
    })
    result_dict = result.to_dict()
    assert result_dict['recid'] == record_id
    assert 'links' in result_dict
    assert NotifyInboxModel.query.count() == 1


def test_service_search(test_app, superuser_identity):
    notify_inbox_serv = create_notify_inbox_service()


    # Create multiple inbox records
    record_id_1 = 'record1'
    record_id_2 = 'record2'
    record_id_3 = 'record3'

    # Create test records
    notify_inbox_serv.create(superuser_identity, {
        'raw': create_notification_data(record_id_1), 'recid': record_id_1,
    })
    notify_inbox_serv.create(superuser_identity, {
        'raw': create_notification_data(record_id_2), 'recid': record_id_2,
    })
    notify_inbox_serv.create(superuser_identity, {
        'raw': create_notification_data(record_id_3), 'recid': record_id_3,
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
