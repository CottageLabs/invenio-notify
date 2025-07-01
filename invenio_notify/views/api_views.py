from flask import jsonify
from coarnotify.server import COARNotifyReceipt
from invenio_notify import constants


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
