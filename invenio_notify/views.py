from flask import current_app, request, jsonify
from invenio_administration.views.base import (
    AdminResourceListView, AdminResourceDetailView,
)
from invenio_i18n import lazy_gettext as _
from invenio_oauth2server import require_oauth_scopes, require_api_auth
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.services import RDMRecordService

from coarnotify.server import COARNotifyServerError
from invenio_notify.blueprints import rest_blueprint
from invenio_notify.scopes import inbox_scope
from invenio_notify.services.service import NotifyInboxService


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
        "raw": {"text": _("Raw"), "order": 2, "width": 7},
        "record_id": {"text": _("Record ID"), "order": 3, "width": 1},
        "user_id": {"text": _("User ID"), "order": 4, "width": 1},
        "process_date": {"text": _("Process Date"), "order": 5, "width": 2},
        "created": {"text": _("Created"), "order": 6, "width": 2},
        "updated": {"text": _("Updated"), "order": 7, "width": 2},
    }

    create_view_name = None

    search_config_name = "NOTIFY_SEARCH"

    search_sort_config_name = "NOTIFY_SORT_OPTIONS"


def create_notify_inbox_api_bp(app):
    return app.extensions["invenio-notify"].notify_inbox_resource.as_blueprint()


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
        "raw": {"text": _("Raw"), "order": 2, "width": 7},
        "record_id": {"text": _("Record ID"), "order": 3, "width": 1},
        "user_id": {"text": _("User ID"), "order": 4, "width": 1},
        "process_date": {"text": _("Process Date"), "order": 5, "width": 2},
        "created": {"text": _("Created"), "order": 6, "width": 2},
        "updated": {"text": _("Updated"), "order": 7, "width": 2},
    }


@rest_blueprint.route("/inbox", methods=['POST'])
@require_api_auth()
@require_oauth_scopes(inbox_scope.id)
def inbox():
    """
    Notify inbox for COAR notifications
    input data will be save as raw data in the database
    """

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400


    inbox_service: NotifyInboxService = current_app.extensions["invenio-notify"].notify_inbox_service

    try:
        result = inbox_service.receive_notification(request.get_json())
        return jsonify({"message": "inbox Done", "location": result.location,
                        "status": result.status}), result.status
    except COARNotifyServerError as e:
        current_app.logger.error(f'Error: {e.message}')
        return jsonify({"error": e.message}), e.status
    except PIDDoesNotExistError as e:
        current_app.logger.debug(f'inbox PIDDoesNotExistError {e.pid_type}:{e.pid_value}')
        return jsonify({"error": "Record not found"}), 404
