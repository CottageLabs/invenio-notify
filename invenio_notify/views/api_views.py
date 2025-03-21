from flask import current_app, request, jsonify
from invenio_oauth2server import require_oauth_scopes, require_api_auth
from invenio_pidstore.errors import PIDDoesNotExistError

from coarnotify.server import COARNotifyServerError, COARNotifyReceipt
from invenio_notify import constants
from invenio_notify.blueprints import rest_blueprint
from invenio_notify.scopes import inbox_scope
from invenio_notify.services.service import NotifyInboxService


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
        return response_coar_notify_receipt(result)

    except COARNotifyServerError as e:
        current_app.logger.error(f'Error: {e.message}')
        return response_coar_notify_receipt(COARNotifyReceipt(constants.STATUS_BAD_REQUEST))

    except PIDDoesNotExistError as e:
        current_app.logger.debug(f'inbox PIDDoesNotExistError {e.pid_type}:{e.pid_value}')
        return response_coar_notify_receipt(COARNotifyReceipt(constants.STATUS_NOT_FOUND), msg="Record not found")


def response_coar_notify_receipt(receipt: COARNotifyReceipt, msg=None):
    data = {
        "status": receipt.status,
    }
    if receipt.location:
        data["location"] = receipt.location

    if msg:
        data["message"] = msg
    else:
        if receipt.status == COARNotifyReceipt.ACCEPTED:
            data["message"] = "Accepted"
        elif receipt.status == COARNotifyReceipt.CREATED:
            data["message"] = "Created"
        elif receipt.status == constants.STATUS_NOT_ACCEPTED:
            data["message"] = "Not Accepted"
        elif receipt.status == constants.STATUS_FORBIDDEN:
            data["message"] = "Forbidden"
        elif receipt.status == constants.STATUS_BAD_REQUEST:
            data["message"] = "Bad Request"

    return jsonify(data), receipt.status
