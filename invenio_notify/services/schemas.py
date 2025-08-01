from datetime import datetime, timezone

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import TZDateTime


def create_current_utc_datetime():
    return datetime.now(timezone.utc)

# KTODO remove duplicate created, updated fields

class NotifyInboxSchema(BaseRecordSchema):
    noti_id = fields.String(required=True)
    raw = fields.String(required=True)  # admin page UI does not support dict yet
    recid = fields.String(required=True)

    user_id = fields.Integer(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)

    process_date = TZDateTime(timezone=timezone.utc, format="iso", required=False)


class ApiNotifyInboxSchema(BaseRecordSchema):
    noti_id = fields.String(required=True)
    raw = fields.Dict(required=True)  # raw for api must be a dict
    recid = fields.String(required=True)
    user_id = fields.Integer(required=True)


class EndorsementSchema(BaseRecordSchema):
    record_id = fields.String(required=True)
    reviewer_id = fields.Integer(required=True)
    review_type = fields.String(required=True)
    inbox_id = fields.Integer(required=True)
    result_url = fields.String(required=True)
    reviewer_name = fields.String(required=True)


class ReviewerMapSchema(BaseRecordSchema):
    user_id = fields.Integer(required=True)
    reviewer_id = fields.Integer(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)


class UserSchema(Schema):
    id = fields.Integer(required=True)
    email = fields.String(required=True)


class ReviewerSchema(BaseRecordSchema):
    name = fields.String(required=True)
    actor_id = fields.String(required=False, allow_none=True)
    inbox_url = fields.String(required=False, allow_none=True)
    inbox_api_token = fields.String(required=False, allow_none=True)
    description = fields.String(required=False)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)

    members = fields.List(fields.Nested(UserSchema), required=False, dump_only=True)


class AddMemberSchema(BaseRecordSchema):
    emails = fields.List(fields.String(), required=True)


class DelMemberSchema(BaseRecordSchema):
    user_id = fields.Integer(required=True)


class EndorsementRequestSchema(BaseRecordSchema):
    noti_id = fields.String(required=True)
    record_id = fields.String(required=True)
    reviewer_id = fields.Integer(required=True)
    raw = fields.Dict(required=True)
    latest_status = fields.String(required=True)
    user_id = fields.Integer(required=False)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)


class EndorsementReplySchema(BaseRecordSchema):
    endorsement_request_id = fields.Integer(required=True)
    inbox_id = fields.Integer(required=True)
    status = fields.String(required=True)

    created = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
    updated = TZDateTime(timezone=timezone.utc, format="iso", dump_only=True)
