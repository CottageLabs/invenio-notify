import json

from invenio_records_resources.services.records.results import RecordList

from invenio_notify import proxies
from invenio_notify.records.models import EndorsementModel
from invenio_notify_test.conftest import prepare_test_rdm_record, create_endorsement_service_data
from invenio_notify_test.fixtures.inbox_fixture import create_inbox
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer


def test_model_create(db, superuser_identity, minimal_record, create_reviewer):
    record = prepare_test_rdm_record(db, minimal_record)

    assert EndorsementModel.query.count() == 0
    record_uuid = record.id

    reviewer = create_reviewer()
    data = dict(
        record_id=record_uuid,
        reviewer_id=reviewer.id,
        review_type='endorsement',
        user_id=superuser_identity.id,
        result_url='https://fake.url',
    )
    model = EndorsementModel()
    model.create(data)
    model.commit()



    assert EndorsementModel.query.count() == 1
    new_model = EndorsementModel.query.first()
    assert new_model.review_type == 'endorsement'


def test_service_create(db, superuser_identity, minimal_record, test_app, create_inbox,
                        create_reviewer):
    record = prepare_test_rdm_record(db, minimal_record)
    service = proxies.current_endorsement_service

    assert EndorsementModel.query.count() == 0

    inbox = create_inbox(recid='r1')

    record_id = str(record.id)
    endorsement_service_data = create_endorsement_service_data(
        record_id, inbox.id, superuser_identity.id, create_reviewer().id)
    service.create(superuser_identity, endorsement_service_data)

    assert EndorsementModel.query.count() == 1

    s: RecordList = service.search(superuser_identity)

    hits = list(s.hits)

    assert len(hits) == 1

    assert hits[0]['review_type'] == 'endorsement'

    print(json.dumps(s.to_dict(), indent=2))


def test_service_update(db, superuser_identity, minimal_record, test_app, create_inbox, create_reviewer):
    record = prepare_test_rdm_record(db, minimal_record)
    endo_serv = proxies.current_endorsement_service
    inbox = create_inbox(recid='r1')

    reviewer = create_reviewer()
    endorsement_service_data = create_endorsement_service_data(
        str(record.id), inbox.id, superuser_identity.id, reviewer.id)
    endo_serv.create(superuser_identity, endorsement_service_data)

    endo_record = EndorsementModel.query.all()[0]

    endorsement_service_data2 = create_endorsement_service_data(
        str(record.id), inbox.id, superuser_identity.id, reviewer.id)
    endorsement_service_data2['review_type'] = 'endorsement2'
    endo_serv.update(superuser_identity, endo_record.id, endorsement_service_data2)

    assert EndorsementModel.query.count() == 1

    s: RecordList = endo_serv.search(superuser_identity,
                                       params={'q': 'review_type:endorsement2'},
                                       )

    print(json.dumps(s.to_dict(), indent=2))

    hits = list(s.hits)

    assert len(hits) == 1
