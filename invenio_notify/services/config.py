from invenio_i18n import gettext as _
from invenio_records_resources.services import RecordServiceConfig
from invenio_records_resources.services.records.links import pagination_links

from invenio_notify.records.models import (
    EndorsementModel,
    EndorsementReplyModel,
    EndorsementRequestModel,
    NotifyInboxModel,
    ReviewerMapModel,
    ReviewerModel,
)
from invenio_notify.services.config_utils import DefaultSearchOptions
from invenio_notify.services.links import (
    EndorsementLink,
    IdLink,
    NotifyInboxLink,
)
from invenio_notify.services.policies import (
    AdminPermissionPolicy,
    EndorsementPermissionPolicy,
    NotifyInboxPermissionPolicy,
)
from invenio_notify.services.results import BasicDbModelRecordList
from invenio_notify.services.schemas import (
    AddMemberSchema,
    ApiNotifyInboxSchema,
    DelMemberSchema,
    EndorsementReplySchema,
    EndorsementRequestSchema,
    EndorsementSchema,
    NotifyInboxSchema,
    ReviewerMapSchema,
    ReviewerSchema,
)


class NotifyInboxSearchOptions(DefaultSearchOptions):
    """Search options specific to NotifyInbox."""
    
    sort_default = "created"
    sort_options = {
        # Ascending options
        "id": dict(
            title=_("ID (Ascending)"),
            fields=["id"],
        ),
        "created": dict(
            title=_("Created (Newest First)"),
            fields=["created"],
        ),
        "updated": dict(
            title=_("Updated (Newest First)"),
            fields=["updated"],
        ),
        "process_date": dict(
            title=_("Process Date (Newest First)"),
            fields=["process_date"],
        ),
        "record_id": dict(
            title=_("Record ID (A-Z)"),
            fields=["record_id"],
        ),
        "user_id": dict(
            title=_("User ID (Ascending)"),
            fields=["user_id"],
        ),
        # Descending options (with minus prefix)
        "-id": dict(
            title=_("ID (Descending)"),
            fields=["-id"],
        ),
        "-created": dict(
            title=_("Created (Oldest First)"),
            fields=["-created"],
        ),
        "-updated": dict(
            title=_("Updated (Oldest First)"),
            fields=["-updated"],
        ),
        "-process_date": dict(
            title=_("Process Date (Oldest First)"),
            fields=["-process_date"],
        ),
        "-record_id": dict(
            title=_("Record ID (Z-A)"),
            fields=["-record_id"],
        ),
        "-user_id": dict(
            title=_("User ID (Descending)"),
            fields=["-user_id"],
        ),
    }


class NotifyInboxServiceConfig(RecordServiceConfig):
    """Service factory configuration."""

    result_list_cls = BasicDbModelRecordList
    record_cls = NotifyInboxModel
    schema = NotifyInboxSchema
    schema_api = ApiNotifyInboxSchema

    permission_policy_cls = NotifyInboxPermissionPolicy

    # Search configuration
    search = NotifyInboxSearchOptions

    # # links configuration
    links_item = {
        "self": NotifyInboxLink("{+api}/notify-inbox/{id}"),
    }
    links_search = pagination_links("{+api}/notify-inbox{?args*}")


class EndorsementAdminServiceConfig(RecordServiceConfig):
    result_list_cls = BasicDbModelRecordList
    record_cls = EndorsementModel
    schema = EndorsementSchema
    permission_policy_cls = EndorsementPermissionPolicy

    search = DefaultSearchOptions

    links_item = {
        "self": EndorsementLink("{+api}/endorsement-admin/{id}"),
    }


class ReviewerMapSearchOptions(DefaultSearchOptions):
    sort_default = "user_id"
    sort_options = {
        "user_id": dict(
            title=_("User id"),
            fields=["user_id"],
        ),
        "reviewer_id": dict(
            title=_("Reviewer id"),
            fields=["reviewer_id"],
        ),
    }


class ReviewerMapServiceConfig(RecordServiceConfig):
    result_list_cls = BasicDbModelRecordList
    record_cls = ReviewerMapModel
    schema = ReviewerMapSchema

    permission_policy_cls = AdminPermissionPolicy

    # # Search configuration
    search = ReviewerMapSearchOptions

    # # links configuration
    links_item = {
        "self": IdLink("{+api}/reviewer-map/{id}"),
    }
    links_search = pagination_links("{+api}/reviewer-map{?args*}")


class ReviewerServiceConfig(RecordServiceConfig):
    result_list_cls = BasicDbModelRecordList
    record_cls = ReviewerModel
    schema = ReviewerSchema
    schema_add_member = AddMemberSchema
    schema_del_member = DelMemberSchema

    permission_policy_cls = AdminPermissionPolicy

    # Search configuration
    search = DefaultSearchOptions

    # Links configuration
    links_item = {
        "self": IdLink("{+api}/reviewer/{id}"),
    }
    links_search = pagination_links("{+api}/reviewer{?args*}")


class EndorsementRequestServiceConfig(RecordServiceConfig):
    result_list_cls = BasicDbModelRecordList
    record_cls = EndorsementRequestModel
    schema = EndorsementRequestSchema
    permission_policy_cls = AdminPermissionPolicy

    search = DefaultSearchOptions

    links_item = {
        "self": IdLink("{+api}/endorsement-request/{id}"),
    }
    links_search = pagination_links("{+api}/endorsement-request{?args*}")


class EndorsementReplyServiceConfig(RecordServiceConfig):
    result_list_cls = BasicDbModelRecordList
    record_cls = EndorsementReplyModel
    schema = EndorsementReplySchema
    permission_policy_cls = AdminPermissionPolicy

    search = DefaultSearchOptions

    links_item = {
        "self": IdLink("{+api}/endorsement-reply/{id}"),
    }
    links_search = pagination_links("{+api}/endorsement-reply{?args*}")
