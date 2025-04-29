from invenio_records.systemfields import ModelField
from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField

from invenio_notify.records import models
from invenio_notify.records.systemfields.pidid import PIDIdOnlyField, PID_TYPE_ENDORSEMENT


class EndorsementRecord(Record):
    model_cls = models.EndorsementMetadataModel
    id = ModelField()

    pid = PIDIdOnlyField("id", PID_TYPE_ENDORSEMENT)

    index = IndexField("endorsement-endorsement-v1.0.0",
                       search_alias="endorsement"
                       )
