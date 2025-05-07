from invenio_i18n import gettext as _
from invenio_records_resources.services import RecordServiceConfig
from invenio_records_resources.services.base.config import FromConfig, ConfiguratorMixin
from invenio_records_resources.services.records.links import pagination_links

from invenio_notify.records.models import NotifyInboxModel, ReviewerMapModel, ReviewerModel
from invenio_notify.records.records import EndorsementRecord
from invenio_notify.services.components import DefaultEndorsementComponents
from invenio_notify.services.config_utils import DefaultSearchOptions
from invenio_notify.services.links import EndorsementLink, NotifyInboxLink, IdLink
from invenio_notify.services.policies import NotifyInboxPermissionPolicy, AdminPermissionPolicy, \
    EndorsementPermissionPolicy
from invenio_notify.services.results import BasicDbModelRecordList
from invenio_notify.services.schemas import AddMemberSchema, DelMemberSchema
from invenio_notify.services.schemas import NotifyInboxSchema, EndorsementSchema, ReviewerMapSchema, ReviewerSchema


class NotifyInboxServiceConfig(RecordServiceConfig):
    """Service factory configuration."""

    result_list_cls = BasicDbModelRecordList
    record_cls = NotifyInboxModel
    schema = NotifyInboxSchema

    permission_policy_cls = NotifyInboxPermissionPolicy

    # Search configuration
    search = DefaultSearchOptions

    # # links configuration
    links_item = {
        "self": NotifyInboxLink("{+api}/notify-inbox/{id}"),
    }
    links_search = pagination_links("{+api}/notify-inbox{?args*}")


class EndorsementServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    record_cls = EndorsementRecord
    permission_policy_cls = EndorsementPermissionPolicy

    schema = EndorsementSchema

    links_item = {
        "self": EndorsementLink("{+api}/endorsement/{id}"),  # TODO to be updated
    }
    # components =  DefaultEndorsementComponents
    components = FromConfig(
        "ENDORSEMENT_SERVICE_COMPONENTS", default=DefaultEndorsementComponents
    )


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
