import uuid
from copy import deepcopy
from unittest.mock import patch

from coarnotify.factory import COARNotifyFactory
from invenio_notify.utils.endorsement_request_utils import create_endorsement_request_data


class TestCreateEndorsementRequestData:
    """Test suite for create_endorsement_request_data function."""

    @patch('invenio_notify.utils.endorsement_request_utils.invenio_url_for')
    @patch('invenio_notify.utils.endorsement_request_utils.uuid.uuid4')
    def test_basic_functionality(self, mock_uuid, mock_url_for, rdm_record, superuser, create_actor):
        """Test basic endorsement request data creation with DOI links."""
        # Setup mocks
        test_uuid = uuid.UUID('12345678-1234-5678-9012-123456789012')
        mock_uuid.return_value = test_uuid
        mock_url_for.return_value = 'https://example.com/inbox'

        # Create test objects
        user = superuser
        record_item = rdm_record  # rdm_record fixture already returns RecordItem
        actor = create_actor(
            actor_id='https://fake.dev.abc/test-actor',
            name='Test Actor',
            inbox_url='https://actor.example.com/inbox'
        )

        # Add DOI to record data
        record_item.data['links']['doi'] = 'https://doi.org/10.1234/test.doi'

        # Call function with origin_id
        origin_id = 'https://example.com/origin'
        result = create_endorsement_request_data(user, record_item, actor, origin_id)

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

        # Verify HTML record page is included (new behavior)
        assert 'ietf:item' in result['object']
        assert result['object']['ietf:item']['id'] == record_item.data['links']['self_html']
        assert result['object']['ietf:item']['mediaType'] == 'text/html'
        assert result['object']['ietf:item']['type'] == ['Page', 'sorg:AboutPage']

        # Verify DOI is included
        assert result['object']['ietf:cite-as'] == 'https://doi.org/10.1234/test.doi'

        # Verify origin and target
        assert result['origin']['id'] == origin_id
        assert result['origin']['inbox'] == 'https://example.com/inbox'
        assert result['origin']['type'] == 'Service'

        assert result['target']['id'] == actor.actor_id
        assert result['target']['inbox'] == actor.inbox_url
        assert result['target']['type'] == 'Service'

        # test coar validation
        COARNotifyFactory.get_by_object(deepcopy(result)).to_jsonld()
