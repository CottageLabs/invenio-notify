from datetime import timezone, datetime

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import fields, Schema
from marshmallow_utils.fields import TZDateTime, NestedAttribute


def create_current_utc_datetime():
    return datetime.now(timezone.utc)


class NotifyInboxSchema(BaseRecordSchema):
    raw = fields.String(required=True)
    recid = fields.String(required=True)

    user_id = fields.Integer(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)

    process_date = TZDateTime(timezone=timezone.utc, format="iso", required=False)


class EndorsementMetadataSchema(Schema):
    # TODO review fields
    record_id = fields.String(required=True)

    record_url = fields.String(required=True)
    result_url = fields.String(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True,
                         load_default=create_current_utc_datetime,
                         dump_default=create_current_utc_datetime,
                         )
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True,
                         load_default=create_current_utc_datetime,
                         dump_default=create_current_utc_datetime,
                         )


class EndorsementSchema(BaseRecordSchema):
    # TODO review fields
    metadata = NestedAttribute(EndorsementMetadataSchema, required=True)

    record_id = fields.String(required=True)
    reviewer_id = fields.String(required=True)
    review_type = fields.String(required=True)
    user_id = fields.Integer(required=True)
    inbox_id = fields.Integer(required=True)


class ReviewerMapSchema(BaseRecordSchema):
    user_id = fields.Integer(required=True)
    reviewer_id = fields.String(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
