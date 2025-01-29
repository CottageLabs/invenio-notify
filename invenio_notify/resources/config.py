import marshmallow as ma
from flask_resources import JSONDeserializer, RequestBodyParser
from invenio_records_resources.resources import (
    RecordResourceConfig,
    SearchRequestArgsSchema,
)

class NotifyInboxSearchRequestArgsSchema(SearchRequestArgsSchema):
    """NotifyInbox request parameters."""

    sort_direction = ma.fields.Str()


class NotifyInboxResourceConfig(RecordResourceConfig):

    blueprint_name = "notify_inbox"
    url_prefix = "/notify-inbox"
    routes = {
        "item": "/<notify_inbox_id>",
        "list": "/",
    }

    request_view_args = {
        "notify_inbox_id": ma.fields.String(),
    }

    # request_extra_args = {
    #     "active": ma.fields.Boolean(),
    #     "url_path": ma.fields.String(),
    # }

    request_search_args = NotifyInboxSearchRequestArgsSchema

    request_body_parsers = {"application/json": RequestBodyParser(JSONDeserializer())}
    default_content_type = "application/json"

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }
