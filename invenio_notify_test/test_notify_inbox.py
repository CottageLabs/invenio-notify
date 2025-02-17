import pytest

from invenio_notify.errors import NotExistsError
from invenio_notify.records.models import NotifyInboxModel
from invenio_notify.services.config import NotifyInboxServiceConfig
from invenio_notify.services.service import NotifyInboxService


def create_notify_inbox_service():
    return NotifyInboxService(config=NotifyInboxServiceConfig)



def test_create_model(db):
    assert NotifyInboxModel.query.count() == 0
    record_id = 'kajsdlkasjk'
    m = NotifyInboxModel.create({'raw': 'test', 'record_id': record_id})
    m.commit()

    # find record by record_id
    new_m = NotifyInboxModel.search({'record_id': record_id}, [])
    assert m == new_m[0]
    assert NotifyInboxModel.query.count() == 1


def test_service_create(test_app, superuser_identity):
    notify_inbox_serv = create_notify_inbox_service()

    assert NotifyInboxModel.query.count() == 0
    record_id = 'kajsdlkasjk'
    result = notify_inbox_serv.create(superuser_identity, {'raw': 'test', 'record_id': record_id})
    result_dict = result.to_dict()
    assert result_dict['record_id'] == record_id
    assert 'links' in result_dict
    assert NotifyInboxModel.query.count() == 1


def test_delete(test_app, superuser_identity):
    notify_inbox_serv = create_notify_inbox_service()

    m = NotifyInboxModel.create({'raw': 'test', 'record_id': 'kajsdlkasjk'})
    assert NotifyInboxModel.query.count() == 1
    notify_inbox_serv.delete(superuser_identity, m.id)
    assert NotifyInboxModel.query.count() == 0


def test_delete__not_exists(test_app, superuser_identity):
    notify_inbox_serv = create_notify_inbox_service()

    with pytest.raises(NotExistsError):
        notify_inbox_serv.delete(superuser_identity, 1)
