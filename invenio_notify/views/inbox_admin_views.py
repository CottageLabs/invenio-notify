from flask_babel import lazy_gettext as _
from invenio_administration.views.base import AdminResourceListView, AdminResourceDetailView


class NotifyInboxListView(AdminResourceListView):
    """Search admin view."""

    api_endpoint = "/notify-inbox"
    name = "notify-inbox"
    resource_config = "notify_inbox_resource"
    title = "Notify Inbox"
    menu_label = "Notify Inbox"
    category = _("Notify Inbox")
    pid_path = "id"
    icon = "newspaper"

    display_search = True
    display_delete = True
    display_create = False
    display_edit = False

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "noti_id": {"text": _("Notification ID"), "order": 2, "width": 2},
        "raw": {"text": _("Raw"), "order": 3, "width": 6},
        "recid": {"text": _("Record ID"), "order": 4, "width": 1},
        "user_id": {"text": _("User ID"), "order": 5, "width": 1},
        "process_date": {"text": _("Process Date"), "order": 6, "width": 2},
        "process_note": {"text": _("Process Note"), "order": 7, "width": 2},
        "created": {"text": _("Created"), "order": 8, "width": 2},
        "updated": {"text": _("Updated"), "order": 9, "width": 2},
    }

    create_view_name = None

    search_config_name = "NOTIFY_SEARCH"

    search_sort_config_name = "NOTIFY_SORT_OPTIONS"


class NotifyInboxDetailView(AdminResourceDetailView):
    """Admin notify inbox detail view."""

    url = "/notify-inbox/<pid_value>"
    api_endpoint = "/notify-inbox"
    name = "notify-inbox-details"
    resource_config = "notify_inbox_resource"
    title = "Notify Inbox Details"

    display_delete = True
    display_edit = False

    list_view_name = "notify-inbox"
    pid_path = "id"

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "noti_id": {"text": _("Notification ID"), "order": 2, "width": 2},
        "raw": {"text": _("Raw"), "order": 3, "width": 6},
        "recid": {"text": _("Record ID"), "order": 4, "width": 1},
        "user_id": {"text": _("User ID"), "order": 5, "width": 1},
        "process_date": {"text": _("Process Date"), "order": 6, "width": 2},
        "process_note": {"text": _("Process Note"), "order": 7, "width": 2},
        "created": {"text": _("Created"), "order": 8, "width": 2},
        "updated": {"text": _("Updated"), "order": 9, "width": 2},
    }
