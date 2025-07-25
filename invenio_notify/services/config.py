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


class NotifyInboxServiceConfig(RecordServiceConfig):
    """Service factory configuration."""

    result_list_cls = BasicDbModelRecordList
    record_cls = NotifyInboxModel
    schema = NotifyInboxSchema
    schema_api = ApiNotifyInboxSchema

    permission_policy_cls = NotifyInboxPermissionPolicy

    # Search configuration
    search = DefaultSearchOptions

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
