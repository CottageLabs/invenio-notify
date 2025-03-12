import json
from invenio_records_resources.services.records.results import RecordList

from invenio_notify.records.models import EndorsementMetadataModel, NotifyInboxModel
from invenio_notify.records.records import EndorsementRecord
from invenio_notify.services.config import EndorsementServiceConfig
from invenio_notify.services.service import EndorsementService
from invenio_notify_test.conftest import prepare_test_rdm_record, create_endorsement_service_data


def test_model_create(db, superuser_identity, minimal_record):
    record = prepare_test_rdm_record(db, minimal_record)

    assert EndorsementMetadataModel.query.count() == 0
    record_uuid = record.id
    data = {
        'field_a': 'some random data for frontend',
    }
    model = EndorsementMetadataModel(
        data=data,
        record_id=record_uuid,
        reviewer_id='reviewer-123',
        review_type='endorsement',
        user_id=superuser_identity.id
    )
    model.create()
    model.commit()

    assert EndorsementMetadataModel.query.count() == 1

    new_model = model.get(model.id)
    assert new_model.json == data


def test_service_create(db, superuser_identity, minimal_record, test_app):
    record = prepare_test_rdm_record(db, minimal_record)
    service = EndorsementService(EndorsementServiceConfig.build(test_app))

    assert EndorsementMetadataModel.query.count() == 0

    # inbox = NotifyInboxModel.create({})
    inbox = NotifyInboxModel.create({'raw': 'test', 'record_id': 'r1', 'user_id': superuser_identity.id})

    record_id = str(record.id)
    endorsement_service_data = create_endorsement_service_data(record_id, inbox.id, superuser_identity.id)
    service.create(superuser_identity, endorsement_service_data)

    assert EndorsementMetadataModel.query.count() == 1

    EndorsementRecord.index.refresh()

    s: RecordList = service.search(superuser_identity)

    hits = list(s.hits)

    assert len(hits) == 1

    assert hits[0]['metadata']['record_id'] == record_id

    print(json.dumps(s.to_dict(), indent=2))


def test_service_update(db, superuser_identity, minimal_record, test_app):
    record = prepare_test_rdm_record(db, minimal_record)
    end_service = EndorsementService(EndorsementServiceConfig.build(test_app))
    inbox = NotifyInboxModel.create({'raw': 'test', 'record_id': 'r1', 'user_id': superuser_identity.id})

    endorsement_service_data = create_endorsement_service_data(str(record.id), inbox.id, superuser_identity.id)
    end_service.create(superuser_identity, endorsement_service_data)

    record = EndorsementMetadataModel.query.all()[0]
    record: EndorsementMetadataModel
    print(record)

    endorsement_service_data2 = create_endorsement_service_data(str(record.id), inbox.id, superuser_identity.id)
    endorsement_service_data2['metadata']['record_id'] = 'r2'
    end_service.update(superuser_identity, record.id, endorsement_service_data2)

    assert EndorsementMetadataModel.query.count() == 1

    EndorsementRecord.index.refresh()

    s: RecordList = end_service.search(superuser_identity,
                                       params={'q': 'metadata.record_id:r2'},
                                       )

    print(json.dumps(s.to_dict(), indent=2))

    hits = list(s.hits)

    assert len(hits) == 1
