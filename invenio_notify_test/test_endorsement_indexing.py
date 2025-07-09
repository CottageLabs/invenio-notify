"""Test endorsement indexing functionality."""

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_search import current_search_client

from invenio_notify.constants import TYPE_ENDORSEMENT, TYPE_REVIEW
from invenio_notify.records.models import EndorsementModel, ReviewerModel
from invenio_notify_test.conftest import prepare_test_rdm_record


def test_record_indexing_with_endorsements(db, superuser_identity, minimal_record, 
                                         resource_type_v, location):
    """Test that a record with endorsements gets indexed with non-empty endorsements array."""
    # Create a test record
    record = prepare_test_rdm_record(db, minimal_record)
    
    # Create a reviewer
    reviewer = ReviewerModel.create({
        'name': 'Test Reviewer Service',
        'actor_id': 'test-reviewer-123'
    })
    db.session.commit()
    
    # Create an endorsement for the record
    endorsement_data = {
        'record_id': record.id,
        'reviewer_id': reviewer.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://test-reviewer.example.com/endorsement/123',
        'reviewer_name': reviewer.name,
    }
    
    endorsement = EndorsementModel.create(endorsement_data)
    db.session.commit()
    
    # Verify the endorsement was created
    assert EndorsementModel.query.count() == 1
    
    # Index the record (this should trigger the EndorsementsDumperExt)
    current_rdm_records_service.indexer.index(record)
    
    # Refresh the search index to ensure data is available
    current_search_client.indices.refresh(index="_all")
    
    # Fetch the indexed document
    doc_id = str(record.id)
    index_name = current_rdm_records_service.indexer.record_to_index(record)
    
    # Get the document from the search index
    response = current_search_client.get(index=index_name, id=doc_id)
    indexed_doc = response['_source']
    
    # Assert that the endorsements field exists and is not empty
    assert 'endorsements' in indexed_doc
    assert isinstance(indexed_doc['endorsements'], list)
    assert len(indexed_doc['endorsements']) > 0
    
    # Verify the structure of the endorsements data
    endorsement_data = indexed_doc['endorsements'][0]
    assert 'reviewer_id' in endorsement_data
    assert 'reviewer_name' in endorsement_data
    assert 'endorsement_count' in endorsement_data
    assert 'review_count' in endorsement_data
    assert 'endorsement_list' in endorsement_data
    
    # Verify the endorsement details
    assert endorsement_data['reviewer_id'] == reviewer.id
    assert endorsement_data['reviewer_name'] == reviewer.name
    assert endorsement_data['endorsement_count'] == 1
    assert endorsement_data['review_count'] == 0
    assert len(endorsement_data['endorsement_list']) == 1
    
    # Verify the endorsement list item structure
    endorsement_item = endorsement_data['endorsement_list'][0]
    assert 'created' in endorsement_item
    assert 'url' in endorsement_item
    assert endorsement_item['url'] == 'https://test-reviewer.example.com/endorsement/123'


def test_record_indexing_with_mixed_endorsements_and_reviews(db, superuser_identity, 
                                                           minimal_record, resource_type_v, 
                                                           location):
    """Test that a record with both endorsements and reviews gets indexed correctly."""
    # Create a test record
    record = prepare_test_rdm_record(db, minimal_record)
    
    # Create a reviewer
    reviewer = ReviewerModel.create({
        'name': 'Mixed Review Service',
        'actor_id': 'mixed-reviewer-456'
    })
    db.session.commit()
    
    # Create an endorsement
    endorsement_data = {
        'record_id': record.id,
        'reviewer_id': reviewer.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://mixed-reviewer.example.com/endorsement/456',
        'reviewer_name': reviewer.name,
    }
    
    # Create a review
    review_data = {
        'record_id': record.id,
        'reviewer_id': reviewer.id,
        'review_type': TYPE_REVIEW,
        'result_url': 'https://mixed-reviewer.example.com/review/456',
        'reviewer_name': reviewer.name,
    }
    
    EndorsementModel.create(endorsement_data)
    EndorsementModel.create(review_data)
    db.session.commit()
    
    # Verify both records were created
    assert EndorsementModel.query.count() == 2
    
    # Index the record
    current_rdm_records_service.indexer.index(record)
    current_search_client.indices.refresh(index="_all")
    
    # Fetch the indexed document
    doc_id = str(record.id)
    index_name = current_rdm_records_service.indexer.record_to_index(record)
    response = current_search_client.get(index=index_name, id=doc_id)
    indexed_doc = response['_source']
    
    # Assert that the endorsements field exists and contains both types
    assert 'endorsements' in indexed_doc
    assert len(indexed_doc['endorsements']) == 1  # One reviewer entry
    
    endorsement_data = indexed_doc['endorsements'][0]
    assert endorsement_data['endorsement_count'] == 1
    assert endorsement_data['review_count'] == 1
    assert len(endorsement_data['endorsement_list']) == 1
    assert len(endorsement_data['review_list']) == 1
    
    # Verify URLs are correct
    assert endorsement_data['endorsement_list'][0]['url'] == 'https://mixed-reviewer.example.com/endorsement/456'
    assert endorsement_data['review_list'][0]['url'] == 'https://mixed-reviewer.example.com/review/456'


def test_record_indexing_with_multiple_reviewers(db, superuser_identity, minimal_record, 
                                               resource_type_v, location):
    """Test that a record with endorsements from multiple reviewers gets indexed correctly."""
    # Create a test record
    record = prepare_test_rdm_record(db, minimal_record)
    
    # Create two reviewers
    reviewer1 = ReviewerModel.create({
        'name': 'First Reviewer Service',
        'actor_id': 'first-reviewer-789'
    })
    
    reviewer2 = ReviewerModel.create({
        'name': 'Second Reviewer Service', 
        'actor_id': 'second-reviewer-789'
    })
    db.session.commit()
    
    # Create endorsements from both reviewers
    endorsement1_data = {
        'record_id': record.id,
        'reviewer_id': reviewer1.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://first-reviewer.example.com/endorsement/789',
        'reviewer_name': reviewer1.name,
    }
    
    endorsement2_data = {
        'record_id': record.id,
        'reviewer_id': reviewer2.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://second-reviewer.example.com/endorsement/789',
        'reviewer_name': reviewer2.name,
    }
    
    EndorsementModel.create(endorsement1_data)
    EndorsementModel.create(endorsement2_data)
    db.session.commit()
    
    # Index the record
    current_rdm_records_service.indexer.index(record)
    current_search_client.indices.refresh(index="_all")
    
    # Fetch the indexed document
    doc_id = str(record.id)
    index_name = current_rdm_records_service.indexer.record_to_index(record)
    response = current_search_client.get(index=index_name, id=doc_id)
    indexed_doc = response['_source']
    
    # Assert that the endorsements field contains both reviewers
    assert 'endorsements' in indexed_doc
    assert len(indexed_doc['endorsements']) == 2
    
    # Get reviewer names from the indexed data
    reviewer_names = [e['reviewer_name'] for e in indexed_doc['endorsements']]
    assert 'First Reviewer Service' in reviewer_names
    assert 'Second Reviewer Service' in reviewer_names
    
    # Verify each reviewer has one endorsement
    for endorsement_data in indexed_doc['endorsements']:
        assert endorsement_data['endorsement_count'] == 1
        assert endorsement_data['review_count'] == 0
        assert len(endorsement_data['endorsement_list']) == 1