#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from datetime import datetime, timezone

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import Schema, fields, pre_load, validate, EXCLUDE
from marshmallow_utils.fields import TZDateTime, EDTFDateTimeString, SanitizedUnicode
from marshmallow.fields import URL


def create_current_utc_datetime():
    return datetime.now(timezone.utc)


class NotifyInboxSchema(BaseRecordSchema):
    notification_id = fields.String(required=True)
    raw = fields.String(required=True)  # admin page UI does not support dict yet
    record_id = fields.String(required=True)

    user_id = fields.Integer(required=True)

    process_date = TZDateTime(timezone=timezone.utc, format="iso", required=False)
    process_note = fields.String(required=False)


class ApiNotifyInboxSchema(BaseRecordSchema):
    notification_id = fields.String(required=True)
    raw = fields.Dict(required=True)  # raw for api must be a dict
    record_id = fields.String(required=True)
    user_id = fields.Integer(required=True)


class EndorsementAdminSchema(BaseRecordSchema):
    record_id = fields.String(required=True)
    parent_id = fields.String(required=True)
    actor_id = fields.Integer(required=True)
    review_type = fields.String(required=True)
    inbox_id = fields.Integer(required=True)
    result_url = fields.String(required=True)
    actor_name = fields.String(required=True)
    endorsement_reply_id = fields.Integer(required=False, allow_none=True)



class ActorMapSchema(BaseRecordSchema):
    user_id = fields.Integer(required=True)
    actor_id = fields.Integer(required=True)


class UserSchema(Schema):
    id = fields.Integer(required=True)
    email = fields.String(required=True)


class ActorSchema(BaseRecordSchema):
    name = fields.String(required=True)
    actor_id = fields.String(required=False, allow_none=True)
    inbox_url = fields.Url(schemes={'http', 'https'}, require_tld=True, required=False, allow_none=True)
    inbox_api_token = fields.String(required=False, allow_none=True)
    description = fields.String(required=False)

    members = fields.List(fields.Nested(UserSchema), required=False, dump_only=True)

    @pre_load
    def process_empty_strings(self, data, **kwargs):
        if 'inbox_url' in data and data['inbox_url'] == '':
            data['inbox_url'] = None
        if 'inbox_api_token' in data and data['inbox_api_token'] == '':
            data['inbox_api_token'] = None
        return data


class AddMemberSchema(BaseRecordSchema):
    emails = fields.List(fields.String(), required=True)


class DelMemberSchema(BaseRecordSchema):
    user_id = fields.Integer(required=True)


class EndorsementRequestSchema(BaseRecordSchema):
    notification_id = fields.String(required=True)
    record_id = fields.String(required=True)
    actor_id = fields.Integer(required=True)
    raw = fields.String(required=True)
    latest_status = fields.String(required=True)
    user_id = fields.Integer(required=False)


class EndorsementReplySchema(BaseRecordSchema):
    endorsement_request_id = fields.Integer(required=True)
    inbox_id = fields.Integer(required=True)
    status = fields.String(required=True)


class ActorItemSchema(Schema):

    """Schema for actor item details (endorsements and reviews)."""
    created = EDTFDateTimeString(dump_only=True)
    url = URL(dump_only=True)
    index = fields.Integer(dump_only=True)


class EndorsementSchema(Schema):
    """Schema for endorsements."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    actor_id = fields.Integer(required=True)
    review_count = fields.Integer()
    actor_name = SanitizedUnicode(required=True)
    endorsement_list = fields.List(fields.Nested(ActorItemSchema), required=True)
    endorsement_count = fields.Integer(validate=validate.Range(min=0))
    review_list = fields.List(fields.Nested(ActorItemSchema), required=True)


class NotifySchema(Schema):
    """Schema for notification settings."""
    has_reviews = fields.Boolean()