from invenio_db.uow import unit_of_work

from invenio_notify.records.models import EndorsementRequestModel
from .base_service import BasicDbService


class EndorsementReplyService(BasicDbService):
    """Service for managing endorsement replies."""

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        if filter_maker is None:
            def filter_maker(query_param):
                filters = []
                if query_param:
                    filters.extend([
                        self.record_cls.endorsement_request_id == query_param,
                    ])
                return filters

        return super().search(identity, params, search_preference, expand, filter_maker, **kwargs)

    @unit_of_work()
    def create(self, identity, data, raise_errors=True, uow=None):
        """Create a new endorsement reply and optionally update the parent request status."""
        result = super().create(identity, data, raise_errors=raise_errors, uow=uow)

        if 'endorsement_request_id' in data and 'status' in data:
            request_record = EndorsementRequestModel.get(data['endorsement_request_id'])
            EndorsementRequestModel.update(
                {'latest_status': data['status']},
                data['endorsement_request_id']
            )

        return result