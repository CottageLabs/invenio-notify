from datetime import timezone, datetime

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import fields, Schema
from marshmallow_utils.fields import TZDateTime, NestedAttribute


def create_current_utc_datetime():
    return datetime.now(timezone.utc)


class NotifyInboxSchema(BaseRecordSchema):
    raw = fields.String(required=True)
    record_id = fields.String(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)


class EndorsementMetadataSchema(Schema):
    # KTODO choice fields
    record_id = fields.String(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True,
                         load_default=create_current_utc_datetime,
                         dump_default=create_current_utc_datetime,
                         )
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True,
                         load_default=create_current_utc_datetime,
                         dump_default=create_current_utc_datetime,
                         )


class EndorsementSchema(BaseRecordSchema):
    # KTODO choice fields
    metadata = NestedAttribute(EndorsementMetadataSchema, required=True)
