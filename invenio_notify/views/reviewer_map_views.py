from flask_babel import lazy_gettext as _
from invenio_administration.views.base import (
    AdminResourceListView, 
    AdminResourceDetailView, 
    AdminResourceCreateView,
    AdminResourceEditView
)


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
    display_create = True
    display_edit = True

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "user_id": {"text": _("User ID"), "order": 2, "width": 1},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 3, "width": 3},
        "created": {"text": _("Created"), "order": 4, "width": 2},
        "updated": {"text": _("Updated"), "order": 5, "width": 2},
    }

    create_view_name = "reviewer_map_create"

    search_config_name = "NOTIFY_SEARCH"

    search_sort_config_name = "NOTIFY_SORT_OPTIONS"


class ReviewerMapDetailView(AdminResourceDetailView):
    url = "/reviewer-map/<pid_value>"
    api_endpoint = "/reviewer-map"
    name = "reviewer-map-details"
    resource_config = "reviewer_map_resource"
    title = "Reviewer Map Details"

    display_delete = True
    display_edit = True

    list_view_name = "reviewer-map"
    pid_path = "id"

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "user_id": {"text": _("User ID"), "order": 2, "width": 1},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 3, "width": 3},
        "created": {"text": _("Created"), "order": 4, "width": 2},
        "updated": {"text": _("Updated"), "order": 5, "width": 2},
    }


# Common form fields for create and edit views
reviewer_map_form_fields = {
    "user_id": {
        "order": 1,
        "text": _("User ID"),
        "description": _("The ID of the user in the system."),
    },
    "reviewer_id": {
        "order": 2,
        "text": _("Reviewer ID"),
        "description": _("The ID of the reviewer from external system."),
    },
}


class ReviewerMapCreateView(AdminResourceCreateView):
    """Configuration for Reviewer Map create view."""

    name = "reviewer_map_create"
    url = "/reviewer-map/create"
    resource_config = "reviewer_map_resource"
    # pid_path = "id"
    api_endpoint = "/reviewer-map"
    title = "Create Reviewer Map"

    list_view_name = "reviewer-map"

    form_fields = {
        **reviewer_map_form_fields,
    }


class ReviewerMapEditView(AdminResourceEditView):
    """Configuration for Reviewer Map edit view."""

    name = "reviewer_map_edit"
    url = "/reviewer-map/<pid_value>/edit"
    resource_config = "reviewer_map_resource"
    pid_path = "id"
    api_endpoint = "/reviewer-map"
    title = "Edit Reviewer Map"

    list_view_name = "reviewer-map"

    form_fields = {
        **reviewer_map_form_fields,
        "created": {"order": 3},
        "updated": {"order": 4},
    }
