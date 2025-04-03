from invenio_administration.generators import Administration
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import SystemProcess

from invenio_notify.permissions import Coarnotify


class NotifyInboxPermissionPolicy(BasePermissionPolicy):
    can_create = [Coarnotify(), SystemProcess()]
    can_read = [Coarnotify(), SystemProcess()]
    can_search = [Coarnotify(), SystemProcess()]
    can_update = [Coarnotify(), SystemProcess()]
    can_delete = [Coarnotify(), SystemProcess()]
    can_disable = [Coarnotify(), SystemProcess()]


class AdminPermissionPolicy(BasePermissionPolicy):
    # TODO to be review
    can_create = [Administration(), SystemProcess()]
    can_read = [Administration(), SystemProcess()]
    can_search = [Administration(), SystemProcess()]
    can_update = [Administration(), SystemProcess()]
    can_delete = [Administration(), SystemProcess()]
    can_disable = [Administration(), SystemProcess()]


class ReviewerMapPermissionPolicy(AdminPermissionPolicy):
    pass


class EndorsementPermissionPolicy(AdminPermissionPolicy):
    # TODO to be review
    pass

class ReviewerPermissionPolicy(AdminPermissionPolicy):
    pass
