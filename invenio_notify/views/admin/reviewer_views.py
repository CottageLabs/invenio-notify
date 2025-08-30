from flask_babel import lazy_gettext as _
from invenio_administration.views.base import (
    AdminResourceListView,
    AdminResourceDetailView,
    AdminResourceCreateView,
    AdminResourceEditView
)

from invenio_notify.feature_toggle import PCIEndorsementAdminDisabledMixin


class ReviewerListView(PCIEndorsementAdminDisabledMixin, AdminResourceListView):
    api_endpoint = "/reviewer"
    name = "reviewer"
    resource_config = "reviewer_admin_resource"
    title = "Reviewers"
    menu_label = "Reviewers"
    category = _("Notify")
    pid_path = "id"
    icon = "user"

    display_search = True
    display_delete = True
    display_create = True
    display_edit = True

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "name": {"text": _("Name"), "order": 2, "width": 2},
        "actor_id": {"text": _("Actor ID"), "order": 3, "width": 2},
        "inbox_url": {"text": _("Inbox URL"), "order": 4, "width": 2},
        "description": {"text": _("Description"), "order": 5, "width": 3},
        "created": {"text": _("Created"), "order": 6, "width": 2},
        "updated": {"text": _("Updated"), "order": 7, "width": 2},
    }

    create_view_name = "reviewer_create"

    search_config_name = "NOTIFY_REVIEWER_SEARCH"

    search_sort_config_name = "NOTIFY_REVIEWER_SORT_OPTIONS"

    template = "invenio_notify/administration/reviewer_search.html"


class ReviewerDetailView(PCIEndorsementAdminDisabledMixin, AdminResourceDetailView):
    url = "/reviewer/<pid_value>"
    api_endpoint = "/reviewer"
    name = "reviewer-details"
    resource_config = "reviewer_admin_resource"
    title = "Reviewer Details"

    display_delete = True
    display_edit = True

    list_view_name = "reviewer"
    pid_path = "id"

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "name": {"text": _("Name"), "order": 2, "width": 2},
        "actor_id": {"text": _("Actor ID"), "order": 3, "width": 2},
        "inbox_url": {"text": _("Inbox URL"), "order": 4, "width": 2},
        "inbox_api_token": {"text": _("Inbox API Token"), "order": 4, "width": 2},
        "description": {"text": _("Description"), "order": 5, "width": 3},
        "created": {"text": _("Created"), "order": 6, "width": 2},
        "updated": {"text": _("Updated"), "order": 7, "width": 2},
    }


# Common form fields for create and edit views
reviewer_form_fields = {
    "name": {
        "order": 10,
        "text": _("Name"),
        "description": _("Full name of the reviewer."),
    },
    "actor_id": {
        "order": 20,
        "text": _("Actor ID"),
        "description": _("ID used in COAR notification (JSON)."),
    },
    "inbox_url": {
        "order": 30,
        "text": _("Inbox URL"),
        "description": _("Inbox URL for the reviewer."),
    },
    "inbox_api_token": {
        "order": 35,
        "text": _("Inbox API Token"),
        "description": _("API token for the reviewer's inbox."),
    },
    "description": {
        "order": 40,
        "text": _("Description"),
        "description": _("Additional information about the reviewer."),
    },
}


class ReviewerCreateView(PCIEndorsementAdminDisabledMixin, AdminResourceCreateView):
    """Configuration for Reviewer create view."""

    name = "reviewer_create"
    url = "/reviewer/create"
    resource_config = "reviewer_admin_resource"
    api_endpoint = "/reviewer"
    title = "Create Reviewer"

    list_view_name = "reviewer"

    form_fields = {
        **reviewer_form_fields,
    }


class ReviewerEditView(PCIEndorsementAdminDisabledMixin, AdminResourceEditView):
    """Configuration for Reviewer edit view."""

    name = "reviewer_edit"
    url = "/reviewer/<pid_value>/edit"
    resource_config = "reviewer_admin_resource"
    pid_path = "id"
    api_endpoint = "/reviewer"
    title = "Edit Reviewer"

    list_view_name = "reviewer"

    form_fields = {
        **reviewer_form_fields,
        "created": {"order": 500},
        "updated": {"order": 600},
    }
