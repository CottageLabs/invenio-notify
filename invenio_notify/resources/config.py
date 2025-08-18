import marshmallow as ma
from flask_resources import JSONDeserializer, RequestBodyParser, ResourceConfig, ResponseHandler, JSONSerializer
from invenio_records_resources.resources import (
    RecordResourceConfig,
    SearchRequestArgsSchema,
)
from invenio_records_resources.services.base.config import ConfiguratorMixin


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



class ReviewerResourceConfig(BasicResourceConfig):
    blueprint_name = "reviewer"
    url_prefix = "/reviewer"

    routes = BasicResourceConfig.routes
    # Updated route names for better consistency
    routes['member'] = "/<record_id>/member"
    routes['members'] = "/<record_id>/members"


class InboxApiResourceConfig(RecordResourceConfig):
    """Configuration for the inbox API resource."""
    blueprint_name = "inbox_api"
    url_prefix = ""  # No prefix needed as route is defined directly


class EndorsementRequestResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Configuration for the inbox API resource."""
    blueprint_name = "endorsement_request"
    url_prefix = "/endorsement-request"

    routes = {
        'send': '/send/<path:pid_value>',
        'reviewers': '/reviewers/<path:pid_value>',
    }

    request_view_args = {
        "pid_value": ma.fields.Str(),
    }

    response_handler = {"application/json": ResponseHandler(JSONSerializer())}

