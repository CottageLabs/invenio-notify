import marshmallow as ma
from flask_resources import JSONDeserializer, RequestBodyParser
from invenio_records_resources.resources import (
    RecordResourceConfig,
    SearchRequestArgsSchema,
)


class BasicSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Common search request parameters for basic resources."""

    sort_direction = ma.fields.Str()


class BasicResourceConfig(RecordResourceConfig):
    """Common configuration for all resource configs."""

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


class NotifyInboxResourceConfig(BasicResourceConfig):
    blueprint_name = "notify_inbox"
    url_prefix = "/notify-inbox"
    # request_extra_args = {
    #     "active": ma.fields.Boolean(),
    #     "url_path": ma.fields.String(),
    # }


class ReviewerMapResourceConfig(BasicResourceConfig):
    blueprint_name = "reviewer_map"
    url_prefix = "/reviewer-map"


class ReviewerResourceConfig(BasicResourceConfig):
    blueprint_name = "reviewer"
    url_prefix = "/reviewer"

    routes = BasicResourceConfig.routes
    routes['add-member'] = "/<record_id>/member"

