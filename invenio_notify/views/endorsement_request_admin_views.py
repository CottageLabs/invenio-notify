from flask_babel import lazy_gettext as _
from invenio_administration.views.base import AdminResourceListView, AdminResourceDetailView

from ..feature_toggle import Phase2AdminDisabledMixin


class EndorsementRequestListView(Phase2AdminDisabledMixin, AdminResourceListView):
    """Endorsement request admin list view."""

    api_endpoint = "/endorsement-request-admin"
    name = "endorsement-request"
    resource_config = "endorsement_request_admin_resource"
    title = "Endorsement Requests"
    menu_label = "Endorsement Requests"
    category = _("Notify")
    pid_path = "id"
    icon = "paper plane outline"

    display_search = True
    display_delete = False
    display_create = False
    display_edit = False

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "noti_id": {"text": _("Notification ID"), "order": 2, "width": 2},
        "record_id": {"text": _("Record ID"), "order": 3, "width": 2},
        "user_id": {"text": _("User ID"), "order": 4, "width": 1},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 5, "width": 1},
        "latest_status": {"text": _("Latest Status"), "order": 6, "width": 2},
        "created": {"text": _("Created"), "order": 7, "width": 2},
        "updated": {"text": _("Updated"), "order": 8, "width": 2},
    }

    create_view_name = None

    search_config_name = "NOTIFY_SEARCH"

    search_sort_config_name = "NOTIFY_SORT_OPTIONS"

class EndorsementRequestDetailView(Phase2AdminDisabledMixin, AdminResourceDetailView):
    """Admin endorsement request detail view."""

    url = "/endorsement-request/<pid_value>"
    api_endpoint = "/endorsement-request-admin"
    name = "endorsement-request-details"
    resource_config = "endorsement_request_admin_resource"
    title = "Endorsement Request Details"

    display_delete = False
    display_edit = False

    list_view_name = "endorsement-request"
    pid_path = "id"

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "noti_id": {"text": _("Notification ID"), "order": 2, "width": 2},
        "record_id": {"text": _("Record ID"), "order": 3, "width": 2},
        "user_id": {"text": _("User ID"), "order": 4, "width": 1},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 5, "width": 1},
        "latest_status": {"text": _("Latest Status"), "order": 6, "width": 2},
        "raw": {"text": _("Raw Data"), "order": 7, "width": 6},
        "created": {"text": _("Created"), "order": 8, "width": 2},
        "updated": {"text": _("Updated"), "order": 9, "width": 2},
    }