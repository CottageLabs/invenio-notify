"""Test endorsement indexing functionality."""

from invenio_search import current_search_client

from invenio_notify.constants import TYPE_ENDORSEMENT, TYPE_REVIEW
from invenio_notify.records.models import EndorsementModel, ActorModel
from tests.fixtures.record_fixture import prepare_test_rdm_record
from invenio_rdm_records.proxies import current_rdm_records_service


def test_record_indexing_with_endorsements(db, superuser_identity, minimal_record, 
                                         resource_type_v, location):
    """Test that a record with endorsements gets indexed with non-empty endorsements array."""
    # Create a test record
    record = prepare_test_rdm_record(db, minimal_record)
    
    # Create a actor
    actor = ActorModel.create({
        'name': 'Test Actor Service',
        'actor_id': 'test-actor-123'
    })
    db.session.commit()
    
    # Create an endorsement for the record
    endorsement_data = {
        'record_id': record.id,
        'actor_id': actor.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://test-actor.example.com/endorsement/123',
        'actor_name': actor.name,
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
    assert 'actor_id' in endorsement_data
    assert 'actor_name' in endorsement_data
    assert 'endorsement_count' in endorsement_data
    assert 'review_count' in endorsement_data
    assert 'endorsement_list' in endorsement_data
    
    # Verify the endorsement details
    assert endorsement_data['actor_id'] == actor.id
    assert endorsement_data['actor_name'] == actor.name
    assert endorsement_data['endorsement_count'] == 1
    assert endorsement_data['review_count'] == 0
    assert len(endorsement_data['endorsement_list']) == 1
    
    # Verify the endorsement list item structure
    endorsement_item = endorsement_data['endorsement_list'][0]
    assert 'created' in endorsement_item
    assert 'index' in endorsement_item
    assert 'url' in endorsement_item
    assert endorsement_item['url'] == 'https://test-actor.example.com/endorsement/123'


def test_record_indexing_with_mixed_endorsements_and_reviews(db, superuser_identity, 
                                                           minimal_record, resource_type_v, 
                                                           location):
    """Test that a record with both endorsements and reviews gets indexed correctly."""
    # Create a test record
    record = prepare_test_rdm_record(db, minimal_record)
    
    # Create a actor
    actor = ActorModel.create({
        'name': 'Mixed Review Service',
        'actor_id': 'mixed-actor-456'
    })
    db.session.commit()
    
    # Create an endorsement
    endorsement_data = {
        'record_id': record.id,
        'actor_id': actor.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://mixed-actor.example.com/endorsement/456',
        'actor_name': actor.name,
    }
    
    # Create a review
    review_data = {
        'record_id': record.id,
        'actor_id': actor.id,
        'review_type': TYPE_REVIEW,
        'result_url': 'https://mixed-actor.example.com/review/456',
        'actor_name': actor.name,
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
    assert len(indexed_doc['endorsements']) == 1  # One actor entry
    
    endorsement_data = indexed_doc['endorsements'][0]
    assert endorsement_data['endorsement_count'] == 1
    assert endorsement_data['review_count'] == 1
    assert len(endorsement_data['endorsement_list']) == 1
    assert len(endorsement_data['review_list']) == 1
    
    # Verify URLs are correct
    assert endorsement_data['endorsement_list'][0]['url'] == 'https://mixed-actor.example.com/endorsement/456'
    assert endorsement_data['review_list'][0]['url'] == 'https://mixed-actor.example.com/review/456'


def test_record_indexing_with_multiple_actors(db, superuser_identity, minimal_record, 
                                               resource_type_v, location):
    """Test that a record with endorsements from multiple actors gets indexed correctly."""
    # Create a test record
    record = prepare_test_rdm_record(db, minimal_record)
    
    # Create two actors
    actor1 = ActorModel.create({
        'name': 'First Actor Service',
        'actor_id': 'first-actor-789'
    })
    
    actor2 = ActorModel.create({
        'name': 'Second Actor Service', 
        'actor_id': 'second-actor-789'
    })
    db.session.commit()
    
    # Create endorsements from both actors
    endorsement1_data = {
        'record_id': record.id,
        'actor_id': actor1.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://first-actor.example.com/endorsement/789',
        'actor_name': actor1.name,
    }
    
    endorsement2_data = {
        'record_id': record.id,
        'actor_id': actor2.id,
        'review_type': TYPE_ENDORSEMENT,
        'result_url': 'https://second-actor.example.com/endorsement/789',
        'actor_name': actor2.name,
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
    
    # Assert that the endorsements field contains both actors
    assert 'endorsements' in indexed_doc
    assert len(indexed_doc['endorsements']) == 2
    
    # Get actor names from the indexed data
    actor_names = [e['actor_name'] for e in indexed_doc['endorsements']]
    assert 'First Actor Service' in actor_names
    assert 'Second Actor Service' in actor_names
    
    # Verify each actor has one endorsement
    for endorsement_data in indexed_doc['endorsements']:
        assert endorsement_data['endorsement_count'] == 1
        assert endorsement_data['review_count'] == 0
        assert len(endorsement_data['endorsement_list']) == 1