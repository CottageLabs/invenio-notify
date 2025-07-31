from flask_babel import lazy_gettext as _
from invenio_administration.views.base import AdminResourceListView, AdminResourceDetailView

from ..feature_toggle import Phase1AdminDisabledMixin


class EndorsementListView(Phase1AdminDisabledMixin, AdminResourceListView):
    """Endorsement admin list view."""

    api_endpoint = "/endorsement-admin"
    name = "endorsement"
    resource_config = "endorsement_admin_resource"
    title = "Endorsements"
    menu_label = "Endorsements"
    category = _("Notify")
    pid_path = "id"
    icon = "certificate"

    display_search = True
    display_delete = True
    display_create = False
    display_edit = False

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "record_id": {"text": _("Record ID"), "order": 2, "width": 2},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 3, "width": 1},
        "reviewer_name": {"text": _("Reviewer Name"), "order": 4, "width": 2},
        "review_type": {"text": _("Review Type"), "order": 5, "width": 1},
        "result_url": {"text": _("Result URL"), "order": 6, "width": 2},
        "created": {"text": _("Created"), "order": 7, "width": 2},
        "updated": {"text": _("Updated"), "order": 8, "width": 2},
    }

    create_view_name = None

    search_config_name = "NOTIFY_SEARCH"

    search_sort_config_name = "NOTIFY_SORT_OPTIONS"


class EndorsementDetailView(Phase1AdminDisabledMixin, AdminResourceDetailView):
    """Admin endorsement detail view."""

    url = "/endorsement/<pid_value>"
    api_endpoint = "/endorsement-admin"
    name = "endorsement-details"
    resource_config = "endorsement_admin_resource"
    title = "Endorsement Details"

    display_delete = True
    display_edit = False

    list_view_name = "endorsement"
    pid_path = "id"

    item_field_list = {
        "id": {"text": _("Id"), "order": 1, "width": 1},
        "record_id": {"text": _("Record ID"), "order": 2, "width": 2},
        "reviewer_id": {"text": _("Reviewer ID"), "order": 3, "width": 1},
        "reviewer_name": {"text": _("Reviewer Name"), "order": 4, "width": 2},
        "review_type": {"text": _("Review Type"), "order": 5, "width": 1},
        "result_url": {"text": _("Result URL"), "order": 6, "width": 3},
        "created": {"text": _("Created"), "order": 7, "width": 2},
        "updated": {"text": _("Updated"), "order": 8, "width": 2},
    }