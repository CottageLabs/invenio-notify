from flask_babel import lazy_gettext as _
from invenio_administration.views.base import (
    AdminResourceListView,
    AdminResourceDetailView,
    AdminResourceCreateView,
    AdminResourceEditView
)

from invenio_notify.feature_toggle import PCIEndorsementAdminDisabledMixin


class ActorListView(PCIEndorsementAdminDisabledMixin, AdminResourceListView):
    api_endpoint = "/actor"
    name = "actor"
    resource_config = "actor_admin_resource"
    title = "Actors"
    menu_label = "Actors"
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

    create_view_name = "actor_create"

    search_config_name = "NOTIFY_ACTOR_SEARCH"

    search_sort_config_name = "NOTIFY_ACTOR_SORT_OPTIONS"

    template = "invenio_notify/administration/actor_search.html"


class ActorDetailView(PCIEndorsementAdminDisabledMixin, AdminResourceDetailView):
    url = "/actor/<pid_value>"
    api_endpoint = "/actor"
    name = "actor-details"
    resource_config = "actor_admin_resource"
    title = "Actor Details"

    display_delete = True
    display_edit = True

    list_view_name = "actor"
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
actor_form_fields = {
    "name": {
        "order": 10,
        "text": _("Name"),
        "description": _("Full name of the actor."),
    },
    "actor_id": {
        "order": 20,
        "text": _("Actor ID"),
        "description": _("ID used in COAR notification (JSON)."),
    },
    "inbox_url": {
        "order": 30,
        "text": _("Inbox URL"),
        "description": _("Inbox URL for the actor."),
    },
    "inbox_api_token": {
        "order": 35,
        "text": _("Inbox API Token"),
        "description": _("API token for the actor's inbox."),
    },
    "description": {
        "order": 40,
        "text": _("Description"),
        "description": _("Additional information about the actor."),
    },
}


class ActorCreateView(PCIEndorsementAdminDisabledMixin, AdminResourceCreateView):
    """Configuration for Actor create view."""

    name = "actor_create"
    url = "/actor/create"
    resource_config = "actor_admin_resource"
    api_endpoint = "/actor"
    title = "Create Actor"

    list_view_name = "actor"

    form_fields = {
        **actor_form_fields,
    }


class ActorEditView(PCIEndorsementAdminDisabledMixin, AdminResourceEditView):
    """Configuration for Actor edit view."""

    name = "actor_edit"
    url = "/actor/<pid_value>/edit"
    resource_config = "actor_admin_resource"
    pid_path = "id"
    api_endpoint = "/actor"
    title = "Edit Actor"

    list_view_name = "actor"

    form_fields = {
        **actor_form_fields,
        "created": {"order": 500},
        "updated": {"order": 600},
    }
