import uuid
from unittest.mock import patch

import pytest
from invenio_accounts.models import User

from invenio_notify.utils.endorsement_request_utils import create_endorsement_request_data


@pytest.fixture
def superuser(superuser_identity):
    """Get User object from superuser_identity."""
    return User.query.filter_by(id=superuser_identity.id).first()


class TestCreateEndorsementRequestData:
    """Test suite for create_endorsement_request_data function."""

    @patch('invenio_notify.utils.endorsement_request_utils.invenio_url_for')
    @patch('invenio_notify.utils.endorsement_request_utils.uuid.uuid4')
    def test_basic_functionality(self, mock_uuid, mock_url_for, rdm_record, superuser, create_reviewer):
        """Test basic endorsement request data creation with DOI links."""
        # Setup mocks
        test_uuid = uuid.UUID('12345678-1234-5678-9012-123456789012')
        mock_uuid.return_value = test_uuid
        mock_url_for.return_value = 'https://example.com/inbox'
        
        # Create test objects
        user = superuser
        record_item = rdm_record  # rdm_record fixture already returns RecordItem
        reviewer = create_reviewer(
            actor_id='test-reviewer',
            name='Test Reviewer',
            inbox_url='https://reviewer.example.com/inbox'
        )
        
        # Add DOI to record data
        record_item.data['links']['doi'] = 'https://doi.org/10.1234/test.doi'
        
        # Call function
        result = create_endorsement_request_data(user, record_item, reviewer)
        
        # Verify basic structure
        assert result['@context'] == [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ]
        assert result['id'] == f'urn:uuid:{test_uuid}'
        assert result['type'] == ["Offer", "coar-notify:EndorsementAction"]
        
        # Verify actor
        assert result['actor']['id'] == f'mailto:{user.email}'
        assert result['actor']['name'] == user.username if user.username else user.email
        assert result['actor']['type'] == 'Person'
        
        # Verify object
        assert result['object']['id'] == record_item.data['links']['self_html']
        assert result['object']['type'] == ['Page', 'sorg:AboutPage']
        
        # Verify DOI is included
        assert result['object']['ietf:cite-as'] == 'https://doi.org/10.1234/test.doi'
        
        # Verify origin and target
        assert result['origin']['id'] == 'https://example.com/inbox'
        assert result['origin']['inbox'] == 'https://example.com/inbox'
        assert result['origin']['type'] == 'Service'
        
        assert result['target']['id'] == reviewer.actor_id
        assert result['target']['inbox'] == reviewer.inbox_url
        assert result['target']['type'] == 'Service'

    def test_with_files_as_dict(self, rdm_record, superuser, create_reviewer):
        """Test endorsement request data creation with files as dict with entries."""
        
        # Create test objects
        user = superuser
        record_item = rdm_record  # rdm_record fixture already returns RecordItem
        reviewer = create_reviewer()
        
        # Add files as dict with entries to record data
        record_item.data['files'] = {
            'entries': {
                'file1': {
                    'key': 'research.pdf',
                    'links': {'self': 'https://example.com/files/research.pdf'}
                },
                'file2': {
                    'key': 'readme.txt',
                    'links': {'self': 'https://example.com/files/readme.txt'}
                }
            }
        }
        
        # Call function
        result = create_endorsement_request_data(user, record_item, reviewer)
        
        # Verify PDF file is included
        assert 'ietf:item' in result['object']
        assert result['object']['ietf:item']['id'] == 'https://example.com/files/research.pdf'
        assert result['object']['ietf:item']['mediaType'] == 'application/pdf'
        assert result['object']['ietf:item']['type'] == ['Article', 'sorg:ScholarlyArticle']

    def test_no_files_in_record(self, rdm_record, superuser, create_reviewer):
        """Test endorsement request data creation with no files in record."""
        
        # Create test objects without files
        user = superuser
        record_item = rdm_record  # rdm_record fixture already returns RecordItem
        reviewer = create_reviewer()
        
        # Call function
        result = create_endorsement_request_data(user, record_item, reviewer)
        
        # Verify no ietf:item is included
        assert 'ietf:item' not in result['object']

    def test_no_pdf_files(self, rdm_record, superuser, create_reviewer):
        """Test endorsement request data creation with files but no PDF."""
        
        # Create test objects
        user = superuser
        record_item = rdm_record  # rdm_record fixture already returns RecordItem
        reviewer = create_reviewer()
        
        # Add non-PDF files to record data
        record_item.data['files'] = [
            {
                'key': 'data.txt',
                'links': {'self': 'https://example.com/files/data.txt'}
            },
            {
                'key': 'image.jpg',
                'links': {'self': 'https://example.com/files/image.jpg'}
            }
        ]
        
        # Call function
        result = create_endorsement_request_data(user, record_item, reviewer)
        
        # Verify no ietf:item is included
        assert 'ietf:item' not in result['object']

    def test_missing_file_links(self, rdm_record, superuser, create_reviewer):
        """Test endorsement request data creation with files missing links."""
        
        # Create test objects
        user = superuser
        record_item = rdm_record  # rdm_record fixture already returns RecordItem
        reviewer = create_reviewer()
        
        # Add files without links to record data
        record_item.data['files'] = [
            {
                'key': 'document.pdf'
                # No links property
            },
            {
                'key': 'data.pdf',
                'links': {}  # Empty links
            }
        ]
        
        # Call function
        result = create_endorsement_request_data(user, record_item, reviewer)
        
        # Verify no ietf:item is included due to missing links
        assert 'ietf:item' not in result['object']