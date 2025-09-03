import pytest

from invenio_notify.proxies import (
    current_endorsement_reply_service,
    current_endorsement_request_service,
    current_inbox_service,
    current_notify,
    current_reviewer_service,
)
from invenio_notify_test.fixtures.endorsement_reply_fixture import create_endorsement_reply
from invenio_notify_test.fixtures.endorsement_request_fixture import create_endorsement_request
from invenio_notify_test.fixtures.inbox_fixture import create_inbox
from invenio_notify_test.fixtures.reviewer_fixture import create_reviewer
from invenio_notify_test.fixtures.reviewer_map_fixture import create_reviewer_map
from invenio_notify_test.utils import BasicDbServiceTestHelper


class TestReviewerMapService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_reviewer_map):
        self.create_reviewer_map = create_reviewer_map

    def _create_service(self):
        return current_notify.reviewer_map_service

    def _create_record(self, *args, **kwargs):
        return self.create_reviewer_map()


class TestInboxService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_inbox):
        self.create_inbox = create_inbox

    def _create_service(self):
        return current_inbox_service

    def _create_record(self, *args, **kwargs):
        recid = kwargs.get('recid', 'test-record-id')
        return self.create_inbox(record_id=recid)


class TestReviewerService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_reviewer):
        self.create_reviewer = create_reviewer

    def _create_service(self):
        return current_reviewer_service

    def _create_record(self, *args, **kwargs):
        return self.create_reviewer()


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
