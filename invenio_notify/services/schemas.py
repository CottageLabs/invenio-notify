from datetime import timezone

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import fields, pre_load
from marshmallow_utils.fields import TZDateTime


class NotifyInboxSchema(BaseRecordSchema):
    raw = fields.String(required=True)
    record_id = fields.String(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)

    @pre_load
    def change_none_to_string(self, data, **kwargs):
        """Fix for empty strings not in line with allow_none=True."""
        for field in data:
            if field == "end_datetime" or field == "category":
                if data[field] == "":
                    data[field] = None
        return data
