from flask import current_app, request, jsonify
from invenio_oauth2server import require_oauth_scopes, require_api_auth
from invenio_pidstore.errors import PIDDoesNotExistError

from coarnotify.server import COARNotifyServerError, COARNotifyReceipt
from invenio_notify import constants
from invenio_notify.blueprints import rest_blueprint
from invenio_notify.errors import COARProcessFail
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
        # return jsonify({"error": "Request must be JSON"}), 400
        return create_fail_response(constants.STATUS_BAD_REQUEST, "Request must be JSON")

    inbox_service: NotifyInboxService = current_app.extensions["invenio-notify"].notify_inbox_service

    try:
        result = inbox_service.receive_notification(request.get_json())
        return response_coar_notify_receipt(result)

    except COARNotifyServerError as e:
        current_app.logger.error(f'Error: {e.message}')
        return create_fail_response(constants.STATUS_BAD_REQUEST)

    except COARProcessFail as e:
        return create_fail_response(e.status, e.msg)

    except PIDDoesNotExistError as e:
        current_app.logger.debug(f'inbox PIDDoesNotExistError {e.pid_type}:{e.pid_value}')
        return create_fail_response(constants.STATUS_NOT_FOUND, "Record not found")


def create_default_msg_by_status(status):
    if status == COARNotifyReceipt.ACCEPTED:
        msg = "Accepted"
    elif status == COARNotifyReceipt.CREATED:
        msg = "Created"
    elif status == constants.STATUS_NOT_ACCEPTED:
        msg = "Not Accepted"
    elif status == constants.STATUS_FORBIDDEN:
        msg = "Forbidden"
    elif status == constants.STATUS_BAD_REQUEST:
        msg = "Bad Request"
    elif status == constants.STATUS_NOT_FOUND:
        msg = "Not Found"
    else:
        msg = "Error"
    return msg


def create_fail_response(status, msg=None):
    msg = msg or create_default_msg_by_status(status)
    return jsonify({"status": status, "message": msg}), status


def response_coar_notify_receipt(receipt: COARNotifyReceipt, msg=None):
    data = {
        "status": receipt.status,
    }
    if receipt.location:
        data["location"] = receipt.location

    data["message"] = msg or create_default_msg_by_status(receipt.status)
    return jsonify(data), receipt.status
