import pytest

from invenio_notify.proxies import current_inbox_service, current_reviewer_service, current_notify
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
        return self.create_inbox(recid=recid)
    

class TestReviewerService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_reviewer):
        self.create_reviewer = create_reviewer

    def _create_service(self):
        return current_reviewer_service

    def _create_record(self, *args, **kwargs):
        return self.create_reviewer()

