import marshmallow as ma
from flask_resources import JSONDeserializer, RequestBodyParser
from invenio_records_resources.resources import (
    RecordResourceConfig,
    SearchRequestArgsSchema,
)

class BasicSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Common search request parameters for basic resources."""

    sort_direction = ma.fields.Str()


class NotifyInboxResourceConfig(RecordResourceConfig):

    blueprint_name = "notify_inbox"
    url_prefix = "/notify-inbox"
    routes = {
        "item": "/<record_id>",
        "list": "/",
    }

    request_view_args = {
        "record_id": ma.fields.String(),
    }

    # request_extra_args = {
    #     "active": ma.fields.Boolean(),
    #     "url_path": ma.fields.String(),
    # }

    request_search_args = BasicSearchRequestArgsSchema

    request_body_parsers = {"application/json": RequestBodyParser(JSONDeserializer())}
    default_content_type = "application/json"

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }


class ReviewerMapResourceConfig(RecordResourceConfig):

    blueprint_name = "reviewer_map"
    url_prefix = "/reviewer-map"
    routes = {
        "item": "/<record_id>",
        "list": "/",
    }

    request_view_args = {
        "record_id": ma.fields.String(),
    }

    request_search_args = BasicSearchRequestArgsSchema

    request_body_parsers = {"application/json": RequestBodyParser(JSONDeserializer())}
    default_content_type = "application/json"

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }
