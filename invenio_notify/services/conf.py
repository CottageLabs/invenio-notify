from invenio_administration.generators import Administration
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_resources.services import Link, RecordServiceConfig
from invenio_records_resources.services.records.links import pagination_links

from invenio_notify.records.models import NotifyInboxModel
from invenio_notify.services.results import NotifyInboxRecordList
from invenio_notify.services.schemas import NotifyInboxSchema


class NotifyInboxLink(Link):

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({"id": record.id})


class NotifyInboxPermissionPolicy(BasePermissionPolicy):

    can_create = [AnyUser(), SystemProcess()]
    can_read = [AnyUser(), SystemProcess()]
    can_search = [AnyUser(), SystemProcess()]
    can_update = [Administration(), SystemProcess()]
    can_delete = [AnyUser(), SystemProcess()]
    can_disable = [Administration(), SystemProcess()]


class NotifyInboxServiceConfig(RecordServiceConfig):
    """Service factory configuration."""

    result_list_cls = NotifyInboxRecordList
    record_cls = NotifyInboxModel
    schema = NotifyInboxSchema

    # result_item_cls = BannerItem
    # result_list_cls = BannerList
    permission_policy_cls = NotifyInboxPermissionPolicy
    # schema = BannerSchema
    #
    # # Search configuration
    # search = SearchOptions
    #
    # # links configuration
    links_item = {
        "self": NotifyInboxLink("{+api}/notify-inbox/{id}"),
    }
    links_search = pagination_links("{+api}/notify-inbox{?args*}")
    # record_cls = BannerModel
