import pytest

from invenio_notify_test.reviewer_map_fixture import create_reviewer_map
from invenio_notify_test.test_notify_inbox import create_notify_inbox_service
from invenio_notify_test.test_reviewer_map import create_reviewer_map_service
from invenio_notify_test.utils import BasicDbServiceTestHelper


class TestReviewerMapService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_reviewer_map):
        self.create_reviewer_map = create_reviewer_map

    def _create_service(self):
        return create_reviewer_map_service()

    def _create_record(self, *args, **kwargs):
        return self.create_reviewer_map(reviewer_id='external-reviewer-123')


class TestInboxService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_inbox):
        self.create_inbox = create_inbox

    def _create_service(self):
        return create_notify_inbox_service()

    def _create_record(self, *args, **kwargs):
        recid = kwargs.get('recid', 'test-record-id')
        return self.create_inbox(recid=recid)
