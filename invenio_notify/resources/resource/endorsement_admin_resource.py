from flask_resources import (
    resource_requestctx,
)
from flask_resources import route
from invenio_db.uow import unit_of_work
from invenio_records_resources.resources.records.resource import (
    request_headers,
    request_view_args,
)

from invenio_rdm_records.proxies import current_rdm_records_service
from .basic_db_resource import BasicDbResource
from ...records.models import EndorsementModel, EndorsementReplyModel, EndorsementRequestModel
from ...utils import record_utils


class EndorsementAdminResource(BasicDbResource):

    def create_url_rules(self):
        """Create the URL rules for the endorsement admin resource."""
        routes = self.config.routes
        return [
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
            route("DELETE", routes["item"], self.delete),
        ]

    @request_headers
    @request_view_args
    def delete(self):
        endo_id = resource_requestctx.view_args["record_id"]
        endo_reply = (EndorsementReplyModel.query
                      .join(EndorsementModel, EndorsementReplyModel.id == EndorsementModel.endorsement_reply_id)
                      .filter(EndorsementModel.id == endo_id)
                      .first()
                      )
        result = super().delete()
        if result:
            rdm_record = record_utils.get_rdm_record_by_uuid(result[0]['record_id'])
            current_rdm_records_service.indexer.index(rdm_record)

            if endo_reply:
                delete_endo_reply_with_status(endo_reply)
        return result

    @classmethod
    def find_endo_reply_by_inbox_id(cls, inbox_id):
        """Find endorsement reply by inbox_id."""
        return EndorsementReplyModel.query.filter_by(inbox_id=inbox_id).first()


@unit_of_work()
def delete_endo_reply_with_status(endo_reply, uow=None):
    EndorsementReplyModel.query.filter_by(id=endo_reply.id).delete()
    EndorsementRequestModel.update_latest_status_by_request_id(endo_reply.endorsement_request_id)
