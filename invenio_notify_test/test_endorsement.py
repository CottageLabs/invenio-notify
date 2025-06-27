import json

import pytest
from invenio_records_resources.services.records.results import RecordList
from sqlalchemy.exc import StatementError

from invenio_notify import proxies, constants
from invenio_notify.records.models import EndorsementModel
from invenio_notify_test.conftest import prepare_test_rdm_record
from invenio_notify_test.fixtures.endorsement_fixture import create_endorsement
from invenio_notify_test.fixtures.inbox_fixture import create_inbox
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer


def test_model_create(db, superuser_identity, minimal_record, create_reviewer):
    record = prepare_test_rdm_record(db, minimal_record)

    assert EndorsementModel.query.count() == 0
    reviewer = create_reviewer()
    data = dict(
        record_id=(record.id),
        reviewer_id=reviewer.id,
        review_type='endorsement',
        result_url='https://fake.url',
        reviewer_name=reviewer.name,
    )
    model = EndorsementModel()
    model.create(data)
    model.commit()

    assert EndorsementModel.query.count() == 1
    new_model = EndorsementModel.query.first()
    assert new_model.review_type == 'endorsement'


def test_service_create(db, superuser_identity, minimal_record, test_app, create_inbox,
                        create_reviewer, create_endorsement):
    record = prepare_test_rdm_record(db, minimal_record)
    service = proxies.current_endorsement_service

    assert EndorsementModel.query.count() == 0

    inbox = create_inbox(recid='r1')

    record_id = str(record.id)
    reviewer_id = create_reviewer().id
    create_endorsement(
        record_id=record_id,
        reviewer_id=reviewer_id,
        inbox_id=inbox.id
    )

    assert EndorsementModel.query.count() == 1

    s: RecordList = service.search(superuser_identity)

    hits = list(s.hits)

    assert len(hits) == 1

    assert hits[0]['review_type'] == constants.TYPE_ENDORSEMENT

    print(json.dumps(s.to_dict(), indent=2))


def test_service_update(db, superuser_identity, minimal_record, test_app, create_inbox, create_reviewer,
                        create_endorsement):
    record = prepare_test_rdm_record(db, minimal_record)
    endo_serv = proxies.current_endorsement_service
    inbox = create_inbox(recid='r1')
    reviewer = create_reviewer()

    # Create endorsement data as a dictionary first
    endorsement_data = {
        'record_id': str(record.id),
        'reviewer_id': reviewer.id,
        'inbox_id': inbox.id,
        'review_type': constants.TYPE_ENDORSEMENT,
        'result_url': 'https://example.com/endorsement1',
        'reviewer_name': reviewer.name,
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
                              create_reviewer, create_endorsement):
    """Test the get_endorsement_info method."""
    # Create a record and two reviewers
    record = prepare_test_rdm_record(db, minimal_record)
    not_related_record = prepare_test_rdm_record(db, minimal_record)
    service = proxies.current_endorsement_service
    inbox = create_inbox(recid='r1')

    record_id = str(record.id)
    reviewer1 = create_reviewer(name="Reviewer One")
    reviewer2 = create_reviewer(name="Reviewer Two")

    # Create endorsements using the fixture
    create_endorsement(
        record_id=record_id,
        reviewer_id=reviewer1.id,
        inbox_id=inbox.id,
        review_type=constants.TYPE_ENDORSEMENT,
        result_url='https://example.com/endorsement1'
    )

    create_endorsement(
        record_id=record_id,
        reviewer_id=reviewer1.id,
        inbox_id=inbox.id,
        review_type=constants.TYPE_REVIEW,
        result_url='https://example.com/review1'
    )

    # Create an endorsement for a different record
    create_endorsement(
        record_id=str(not_related_record.id),
        reviewer_id=reviewer1.id,
        inbox_id=inbox.id
    )

    create_endorsement(
        record_id=record_id,
        reviewer_id=reviewer2.id,
        inbox_id=inbox.id,
        result_url='https://example.com/endorsement2'
    )

    # Verify the total number of endorsements
    assert EndorsementModel.query.count() == 4

    # Test get_endorsement_info
    endorsement_info = service.get_endorsement_info(record_id)

    # Verify the structure and content of the result
    assert isinstance(endorsement_info, list)
    assert len(endorsement_info) == 2  # Two reviewers

    # Sort the results by reviewer_id to have a deterministic order for assertions
    sorted_info = sorted(endorsement_info, key=lambda x: x['reviewer_id'])

    # Check first reviewer's endorsement info
    assert sorted_info[0]['reviewer_id'] == reviewer1.id
    assert sorted_info[0]['reviewer_name'] == "Reviewer One"
    assert sorted_info[0]['endorsement_count'] == 1
    assert sorted_info[0]['review_count'] == 1
    assert len(sorted_info[0]['endorsement_list']) == 1
    assert sorted_info[0]['endorsement_list'][0]['url'] == 'https://example.com/endorsement1'
    assert 'created' in sorted_info[0]['endorsement_list'][0]
    assert len(sorted_info[0]['review_list']) == 1
    assert sorted_info[0]['review_list'][0]['url'] == 'https://example.com/review1'
    assert 'created' in sorted_info[0]['review_list'][0]

    # Check second reviewer's endorsement info
    assert sorted_info[1]['reviewer_id'] == reviewer2.id
    assert sorted_info[1]['reviewer_name'] == "Reviewer Two"
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
