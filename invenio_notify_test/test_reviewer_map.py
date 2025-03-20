import pytest

from invenio_notify.records.models import ReviewerMapModel
from invenio_notify.services.config import ReviewerMapServiceConfig
from invenio_notify.services.service import ReviewerMapService
from invenio_notify_test.reviewer_map_fixture import create_reviewer_map
from utils import BasicDbServiceTestHelper


def create_reviewer_map_service():
    return ReviewerMapService(config=ReviewerMapServiceConfig)


def test_create_model(db, superuser_identity):
    assert ReviewerMapModel.query.count() == 0
    reviewer_id = 'external-reviewer-123'

    # Create a new reviewer map entry
    reviewer_map = ReviewerMapModel.create({
        'reviewer_id': reviewer_id,
        'user_id': superuser_identity.id
    })

    # Verify record was created
    assert ReviewerMapModel.query.count() == 1

    # Retrieve the record and verify attributes
    retrieved_map = ReviewerMapModel.get(reviewer_map.id)
    assert retrieved_map.reviewer_id == reviewer_id
    assert retrieved_map.user_id == superuser_identity.id


def test_service_create(test_app, superuser_identity):
    reviewer_map_serv = create_reviewer_map_service()

    assert ReviewerMapModel.query.count() == 0
    reviewer_id = 'external-reviewer-123'

    result = reviewer_map_serv.create(superuser_identity, {
        'reviewer_id': reviewer_id,
        'user_id': superuser_identity.id
    })

    result_dict = result.to_dict()
    assert result_dict['reviewer_id'] == reviewer_id
    assert result_dict['user_id'] == superuser_identity.id
    assert 'links' in result_dict
    assert ReviewerMapModel.query.count() == 1


class TestReviewerMapService(BasicDbServiceTestHelper):

    @pytest.fixture(autouse=True)
    def setup(self, create_reviewer_map):
        self.create_reviewer_map = create_reviewer_map

    def _create_service(self):
        return create_reviewer_map_service()

    def _create_record(self, *args, **kwargs):
        return self.create_reviewer_map(reviewer_id='external-reviewer-123')
