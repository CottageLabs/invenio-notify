#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from copy import deepcopy
from unittest.mock import patch

from coarnotify.patterns import RequestEndorsement
from coarnotify.factory import COARNotifyFactory
from coarnotify.core.activitystreams2 import ActivityStreamsTypes
from invenio_notify.utils.endorsement_request_utils import create_endorsement_request_data


class TestCreateEndorsementRequestData:
    """Test suite for create_endorsement_request_data function."""

    @patch('invenio_notify.utils.endorsement_request_utils.invenio_url_for')
    def test_basic_functionality(self, mock_url_for, rdm_record, superuser, create_actor):
        """Test basic endorsement request data creation with DOI links."""
        # Setup mocks
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
        endorsement: RequestEndorsement = create_endorsement_request_data(user, record_item, actor, origin_id)

        # Verify basic structure
        assert endorsement.namespaces == [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ]
        assert endorsement.id.startswith("urn:uuid:")
        assert endorsement.type == ["Offer", "coar-notify:EndorsementAction"]

        # Verify actor
        assert endorsement.actor.id == f'mailto:{user.email}'
        assert endorsement.actor.name == user.username if user.username else user.email
        assert endorsement.actor.type == 'Person'

        # Verify object
        assert endorsement.object.id == record_item.data['links']['self_html']
        assert endorsement.object.type == ['Page', 'sorg:AboutPage']

        # Verify HTML record page is included (new behavior)
        assert endorsement.object.item.id == record_item.data['links']['self_html']
        assert endorsement.object.item.media_type == 'text/html'
        assert endorsement.object.item.type == ['Page', 'sorg:AboutPage']

        # Verify DOI is included
        assert endorsement.object.cite_as == 'https://doi.org/10.1234/test.doi'

        # Verify origin and target
        assert endorsement.origin.id == origin_id
        assert endorsement.origin.inbox == 'https://example.com/inbox'
        assert endorsement.origin.type == ActivityStreamsTypes.SERVICE

        assert endorsement.target.id == actor.actor_id
        assert endorsement.target.inbox == actor.inbox_url
        assert endorsement.target.type == ActivityStreamsTypes.SERVICE

        # test coar validation
        COARNotifyFactory.get_by_object(deepcopy(endorsement.to_jsonld())).to_jsonld()
