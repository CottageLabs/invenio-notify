import json
from invenio_records_resources.services.records.results import RecordList

from invenio_notify.records.models import EndorsementMetadataModel
from invenio_notify.records.records import EndorsementRecord
from invenio_notify.services.config import EndorsementServiceConfig
from invenio_notify.services.service import EndorsementService


def test_model_create(db):
    assert EndorsementMetadataModel.query.count() == 0
    data = {
        'value_a': 'a',
        'value_b': 'b'
    }
    model = EndorsementMetadataModel(data=data)
    model.create()
    model.commit()

    assert EndorsementMetadataModel.query.count() == 1

    new_model = model.get(model.id)
    assert new_model.json == data


def test_service_create(db, superuser_identity):
    service = EndorsementService(EndorsementServiceConfig)

    assert EndorsementMetadataModel.query.count() == 0

    service.create(superuser_identity, {
        'metadata': {
            'record_id': 'r1'
        }
    })

    assert EndorsementMetadataModel.query.count() == 1

    EndorsementRecord.index.refresh()

    s: RecordList = service.search(superuser_identity)

    hits = list(s.hits)

    assert len(hits) == 1

    assert hits[0]['metadata']['record_id'] == 'r1'

    # print(s.to_dict())
    print(json.dumps(s.to_dict(), indent=2))


def test_service_update(db, superuser_identity):
    service = EndorsementService(EndorsementServiceConfig)

    service.create(superuser_identity, {
        'metadata': {
            'record_id': 'r1'
        }
    })

    record = EndorsementMetadataModel.query.all()[0]
    record: EndorsementMetadataModel
    print(record)

    service.update(superuser_identity, record.id, {
        'metadata': {
            'record_id': 'r2'
        }
    })

    assert EndorsementMetadataModel.query.count() == 1

    EndorsementRecord.index.refresh()

    s: RecordList = service.search(superuser_identity,
                                   params={'q': 'metadata.record_id:r2'},
                                   )

    print(json.dumps(s.to_dict(), indent=2))

    hits = list(s.hits)

    assert len(hits) == 1
