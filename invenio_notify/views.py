import json
from flask import current_app, request, jsonify
from flask import g
from invenio_administration.views.base import (
    AdminResourceListView, AdminResourceDetailView,
)
from invenio_administration.views.base import AdminView
from invenio_i18n import lazy_gettext as _
from invenio_oauth2server import require_oauth_scopes, require_api_auth

from coarnotify.core.notify import NotifyPattern
from coarnotify.server import COARNotifyServiceBinding, COARNotifyReceipt, COARNotifyServer, COARNotifyServerError
from invenio_notify.blueprints import rest_blueprint
from invenio_notify.scopes import inbox_scope
from invenio_notify.services.service import NotifyInboxService


class Pg2View(AdminView):
    """ TOBEREMOVE for study only """
    template = "invenio_notify/pg2.html"
    category = "Playground cat"
    name = "playground"
    url = "/playground"
    icon = "home"
    title = "Playground"
    menu_label = "Playground"


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
        "created": {"text": _("Created"), "order": 3, "width": 2},
        "updated": {"text": _("Updated"), "order": 4, "width": 2},
    }

    # create_view_name = "rawnoti_create"
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
        "created": {"text": _("Created"), "order": 3, "width": 2},
        "updated": {"text": _("Updated"), "order": 4, "width": 2},
    }


@rest_blueprint.route("/hello")
def hello():
    # TOBEREMOVE
    return "Hello, World!"


# TOBEREMOVE
@rest_blueprint.route("/inbox-example", methods=['POST'])
def inbox_example():
    """
    Notify inbox for COAR notifications
    input data will be save as raw data in the database
    """

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    raw = request.get_json()

    print(f'use input raw: {raw}')
    notify_inbox_service: NotifyInboxService = current_app.extensions["invenio-notify"].notify_inbox_service
    notify_inbox_service.create(g.identity, {"raw": json.dumps(raw)})

    return "inbox Done"


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

    raw = request.get_json()

    server = COARNotifyServer(InvnotiCOARNotifyServiceBinding())
    try:
        print(f'input announcement:')
        # rich.print_json(data=announcement.to_jsonld(), highlight=True, indent=4, )
        result = server.receive(raw, validate=True)
        print(f'result: {result}')
        return jsonify({"message": "inbox Done", "location": result.location,
                        "status": result.status}), result.status
    except COARNotifyServerError as e:
        print(f'Error: {e.message}')
        return jsonify({"error": e.message}), e.status


class InvnotiCOARNotifyServiceBinding(COARNotifyServiceBinding):

    def notification_received(self, notification: NotifyPattern) -> COARNotifyReceipt:
        """
        Process an incoming notification object in the following way:

        1. Generate a name for the notification based on the timestamp and a random UUID
        2. Write the notification JSON-LD  to a file in the store directory
        3. Return a receipt for the notification using the configured response status and a location pointing to the file

        :param notification:
        :return:
        """

        print('called notification_received')

        raw = notification.to_jsonld()

        print(f'use input raw: {raw}')
        inbox_service: NotifyInboxService = current_app.extensions["invenio-notify"].notify_inbox_service
        inbox_service.create(g.identity, {"raw": json.dumps(raw)})

        location = 'http://127.0.0.1/tobeimplemented'  # KTODO implement this
        return COARNotifyReceipt(COARNotifyReceipt.CREATED, location)
