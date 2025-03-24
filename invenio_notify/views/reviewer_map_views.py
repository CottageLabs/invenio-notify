from flask_babel import lazy_gettext as _
from invenio_administration.views.base import AdminResourceListView, AdminResourceDetailView


class ReviewerMapListView(AdminResourceListView):
    api_endpoint = "/reviewer-map"
    name = "reviewer-map"
    resource_config = "reviewer_map_resource"
    title = "Reviewer Map"
    menu_label = "Reviewer Map"
    category = _("Notify Inbox")
    pid_path = "id"
    icon = "newspaper"

    display_search = True
    display_delete = True
    display_create = False
    display_edit = False

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "user_id": {"text": _("User ID"), "order": 2, "width": 1},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 3, "width": 3},
        "created": {"text": _("Created"), "order": 4, "width": 2},
        "updated": {"text": _("Updated"), "order": 5, "width": 2},
    }

    create_view_name = None

    search_config_name = "NOTIFY_SEARCH"

    search_sort_config_name = "NOTIFY_SORT_OPTIONS"


class ReviewerMapDetailView(AdminResourceDetailView):
    url = "/reviewer-map/<pid_value>"
    api_endpoint = "/reviewer-map"
    name = "reviewer-map-details"
    resource_config = "reviewer_map_resource"
    title = "Reviewer Map Details"

    display_delete = True
    display_edit = False

    list_view_name = "reviewer-map"
    pid_path = "id"

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "user_id": {"text": _("User ID"), "order": 2, "width": 1},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 3, "width": 3},
        "created": {"text": _("Created"), "order": 4, "width": 2},
        "updated": {"text": _("Updated"), "order": 5, "width": 2},
    }
