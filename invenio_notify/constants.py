"""Constants for the Invenio-Notify module."""

# Notification types
TYPE_REVIEW = 'coar-notify:ReviewAction'
TYPE_ENDORSEMENT = 'coar-notify:EndorsementAction'
SUPPORTED_TYPES = [TYPE_REVIEW, TYPE_ENDORSEMENT]
""" List of supported notification types that can be processed by the notify  """



STATUS_NOT_ACCEPTED = 422
STATUS_BAD_REQUEST = 400
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_SERVER_ERROR = 500

KEY_INBOX_REVIEW_URL = 'ietf:cite-as'
