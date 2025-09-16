import pytest

from invenio_notify.proxies import (
    current_endorsement_reply_service,
    current_endorsement_request_service,
    current_inbox_service,
    current_notify,
    current_actor_service,
)
from invenio_notify_test.fixtures.endorsement_reply_fixture import create_endorsement_reply
from invenio_notify_test.fixtures.endorsement_request_fixture import create_endorsement_request
from invenio_notify_test.fixtures.inbox_fixture import create_inbox
from invenio_notify_test.fixtures.actor_fixture import create_actor
from invenio_notify_test.fixtures.actor_map_fixture import create_actor_map
from invenio_notify_test.utils import BasicDbServiceTestHelper


class TestActorMapService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_actor_map):
        self.create_actor_map = create_actor_map

    def _create_service(self):
        return current_notify.actor_map_service

    def _create_record(self, *args, **kwargs):
        return self.create_actor_map()


class TestInboxService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_inbox):
        self.create_inbox = create_inbox

    def _create_service(self):
        return current_inbox_service

    def _create_record(self, *args, **kwargs):
        record_id = kwargs.get('record_id', 'test-record-id')
        return self.create_inbox(record_id=record_id)


class TestActorService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_actor):
        self.create_actor = create_actor

    def _create_service(self):
        return current_actor_service

    def _create_record(self, *args, **kwargs):
        return self.create_actor()


class TestEndorsementRequestService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_endorsement_request):
        self.create_endorsement_request = create_endorsement_request

    def _create_service(self):
        return current_endorsement_request_service

    def _create_record(self, identity):
        return self.create_endorsement_request()


class TestEndorsementReplyService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_endorsement_reply):
        self.create_endorsement_reply = create_endorsement_reply

    def _create_service(self):
        return current_endorsement_reply_service

    def _create_record(self, identity):
        return self.create_endorsement_reply()
