"""Constants for the Invenio-Notify module."""

# Notification types
TYPE_REVIEW = 'coar-notify:ReviewAction'
TYPE_ENDORSEMENT = 'coar-notify:EndorsementAction'
TYPE_TENTATIVE_ACCEPT = 'TentativeAccept'
TYPE_REJECT = 'Reject'
TYPE_TENTATIVE_REJECT = 'TentativeReject'
SUPPORTED_TYPES = [TYPE_REVIEW, TYPE_ENDORSEMENT, TYPE_TENTATIVE_ACCEPT, TYPE_REJECT, TYPE_TENTATIVE_REJECT]
""" List of supported notification types that can be processed by the notify  """

# Status constants
STATUS_REQUEST_ENDORSEMENT = 'Request Endorsement'



STATUS_NOT_ACCEPTED = 422
STATUS_BAD_REQUEST = 400
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_SERVER_ERROR = 500

KEY_INBOX_REVIEW_URL = 'ietf:cite-as'

# Feature toggle configuration keys
CONFIG_NOTIFY_PHASE_1_ENABLED = 'NOTIFY_PHASE_1_ENABLED'
CONFIG_NOTIFY_PHASE_2_ENABLED = 'NOTIFY_PHASE_2_ENABLED'
