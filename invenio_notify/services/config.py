from invenio_administration.generators import Administration
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import SystemProcess, AnyUser
from invenio_records_resources.services import Link, RecordServiceConfig
from invenio_records_resources.services.base.config import FromConfig, ConfiguratorMixin
from invenio_records_resources.services.records.links import pagination_links

from invenio_notify.permissions import Coarnotify
from invenio_notify.records.models import NotifyInboxModel
from invenio_notify.records.records import EndorsementRecord
from invenio_notify.services.components import DefaultEndorsementComponents
from invenio_notify.services.links import EndorsementLink
from invenio_notify.services.results import NotifyInboxRecordList
from invenio_notify.services.schemas import NotifyInboxSchema, EndorsementSchema


class NotifyInboxLink(Link):

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({"id": record.id})


class NotifyInboxPermissionPolicy(BasePermissionPolicy):
    can_create = [Coarnotify(), SystemProcess()]
    can_read = [Coarnotify(), SystemProcess()]
    can_search = [Coarnotify(), SystemProcess()]
    can_update = [Coarnotify(), SystemProcess()]
    can_delete = [Coarnotify(), SystemProcess()]
    can_disable = [Coarnotify(), SystemProcess()]


class NotifyInboxServiceConfig(RecordServiceConfig):
    """Service factory configuration."""

    result_list_cls = NotifyInboxRecordList
    record_cls = NotifyInboxModel
    schema = NotifyInboxSchema

    # result_item_cls = BannerItem
    # result_list_cls = BannerList
    permission_policy_cls = NotifyInboxPermissionPolicy

    # # Search configuration
    # search = SearchOptions
    #
    # # links configuration
    links_item = {
        "self": NotifyInboxLink("{+api}/notify-inbox/{id}"),
    }
    links_search = pagination_links("{+api}/notify-inbox{?args*}")
    # record_cls = BannerModel


class EndorsementPermissionPolicy(BasePermissionPolicy):
    # TODO to be review
    can_create = [Administration(), SystemProcess()]
    can_read = [Administration(), SystemProcess()]
    can_search = [Administration(), SystemProcess()]
    can_update = [Administration(), SystemProcess()]
    can_delete = [Administration(), SystemProcess()]
    can_disable = [Administration(), SystemProcess()]


class EndorsementServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    record_cls = EndorsementRecord
    permission_policy_cls = EndorsementPermissionPolicy

    schema = EndorsementSchema

    links_item = {
        "self": EndorsementLink("{+api}/endorsement/{id}"),   # TODO to be updated
    }
    # components =  DefaultEndorsementComponents
    components = FromConfig(
        "ENDORSEMENT_SERVICE_COMPONENTS", default=DefaultEndorsementComponents
    )



