import json

import pytest
from invenio_records_resources.services.records.results import RecordList
from sqlalchemy.exc import StatementError

from invenio_notify import proxies, constants
from invenio_notify.records.models import EndorsementModel
from tests.fixtures.endorsement_fixture import create_endorsement
from tests.fixtures.inbox_fixture import create_inbox
from tests.fixtures.record_fixture import prepare_test_rdm_record
from tests.fixtures.actor_fixture import create_actor


def test_model_create(db, superuser_identity, minimal_record, create_actor):
    record = prepare_test_rdm_record(db, minimal_record)

    assert EndorsementModel.query.count() == 0
    actor = create_actor()
    data = dict(
        record_id=(record.id),
        actor_id=actor.id,
        review_type='endorsement',
        result_url='https://fake.url',
        actor_name=actor.name,
    )
    model = EndorsementModel()
    model.create(data)
    model.commit()

    assert EndorsementModel.query.count() == 1
    new_model = EndorsementModel.query.first()
    assert new_model.review_type == 'endorsement'


def test_service_create(db, superuser_identity, minimal_record, test_app, create_inbox,
                        create_actor, create_endorsement):
    record = prepare_test_rdm_record(db, minimal_record)
    service = proxies.current_endorsement_service

    assert EndorsementModel.query.count() == 0

    inbox = create_inbox(record_id='r1')

    record_id = str(record.id)
    actor_id = create_actor().id
    create_endorsement(
        record_id=record_id,
        actor_id=actor_id,
        inbox_id=inbox.id
    )

    assert EndorsementModel.query.count() == 1

    s: RecordList = service.search(superuser_identity)

    hits = list(s.hits)

    assert len(hits) == 1

    assert hits[0]['review_type'] == constants.TYPE_ENDORSEMENT

    print(json.dumps(s.to_dict(), indent=2))


def test_service_update(db, superuser_identity, minimal_record, test_app, create_inbox, create_actor,
                        create_endorsement):
    record = prepare_test_rdm_record(db, minimal_record)
    endo_serv = proxies.current_endorsement_service
    inbox = create_inbox(record_id='r1')
    actor = create_actor()

    # Create endorsement data as a dictionary first
    endorsement_data = {
        'record_id': str(record.id),
        'actor_id': actor.id,
        'inbox_id': inbox.id,
        'review_type': constants.TYPE_ENDORSEMENT,
        'result_url': 'https://example.com/endorsement1',
        'actor_name': actor.name,
    }

    # Create endorsement using the data dictionary
    create_endorsement(**endorsement_data)

    endo_record = EndorsementModel.query.all()[0]

    # Update the review_type in the same data dictionary for the update operation
    endorsement_data['review_type'] = 'endorsement2'

    endo_serv.update(superuser_identity, endo_record.id, endorsement_data)

    assert EndorsementModel.query.count() == 1

    s: RecordList = endo_serv.search(superuser_identity,
                                     params={'q': 'review_type:endorsement2'},
                                     )

    assert len(list(s.hits)) == 1


def test_get_endorsement_info(db, superuser_identity, minimal_record, test_app, create_inbox,
                              create_actor, create_endorsement):
    """Test the get_endorsement_info method."""
    # Create a record and two actors
    record = prepare_test_rdm_record(db, minimal_record)
    not_related_record = prepare_test_rdm_record(db, minimal_record)
    service = proxies.current_endorsement_service

    record_id = str(record.id)
    actor1 = create_actor(name="Actor One")
    actor2 = create_actor(name="Actor Two")

    # Create endorsements using the fixture - each needs unique inbox due to unique constraint
    inbox1 = create_inbox(record_id='r1')
    create_endorsement(
        record_id=record_id,
        actor_id=actor1.id,
        inbox_id=inbox1.id,
        review_type=constants.TYPE_ENDORSEMENT,
        result_url='https://example.com/endorsement1'
    )

    inbox2 = create_inbox(record_id='r2')
    create_endorsement(
        record_id=record_id,
        actor_id=actor1.id,
        inbox_id=inbox2.id,
        review_type=constants.TYPE_REVIEW,
        result_url='https://example.com/review1'
    )

    # Create an endorsement for a different record
    inbox3 = create_inbox(record_id='r3')
    create_endorsement(
        record_id=str(not_related_record.id),
        actor_id=actor1.id,
        inbox_id=inbox3.id
    )

    inbox4 = create_inbox(record_id='r4')
    create_endorsement(
        record_id=record_id,
        actor_id=actor2.id,
        inbox_id=inbox4.id,
        result_url='https://example.com/endorsement2'
    )

    # Verify the total number of endorsements
    assert EndorsementModel.query.count() == 4

    # Test get_endorsement_info
    endorsement_info = service.get_endorsement_info(record.parent.id)

    # Verify the structure and content of the result
    assert isinstance(endorsement_info, list)
    assert len(endorsement_info) == 2  # Two actors

    # Sort the results by actor_id to have a deterministic order for assertions
    sorted_info = sorted(endorsement_info, key=lambda x: x['actor_id'])

    # Check first actor's endorsement info
    assert sorted_info[0]['actor_id'] == actor1.id
    assert sorted_info[0]['actor_name'] == "Actor One"
    assert sorted_info[0]['endorsement_count'] == 1
    assert sorted_info[0]['review_count'] == 1
    assert len(sorted_info[0]['endorsement_list']) == 1
    assert sorted_info[0]['endorsement_list'][0]['url'] == 'https://example.com/endorsement1'
    assert 'created' in sorted_info[0]['endorsement_list'][0]
    assert 'index' in sorted_info[0]['endorsement_list'][0]
    assert len(sorted_info[0]['review_list']) == 1
    assert sorted_info[0]['review_list'][0]['url'] == 'https://example.com/review1'
    assert 'created' in sorted_info[0]['review_list'][0]
    assert 'index' in sorted_info[0]['review_list'][0]

    # Check second actor's endorsement info
    assert sorted_info[1]['actor_id'] == actor2.id
    assert sorted_info[1]['actor_name'] == "Actor Two"
    assert sorted_info[1]['endorsement_count'] == 1
    assert sorted_info[1]['review_count'] == 0
    assert len(sorted_info[1]['endorsement_list']) == 1
    assert sorted_info[1]['endorsement_list'][0]['url'] == 'https://example.com/endorsement2'
    assert 'created' in sorted_info[1]['endorsement_list'][0]
    assert len(sorted_info[1]['review_list']) == 0

    # Test with a non-uuid record ID - should raise StatementError
    with pytest.raises(StatementError):
        service.get_endorsement_info('non-existent-id')

    # Test with None record ID
    none_info = service.get_endorsement_info(None)
    assert none_info == []
