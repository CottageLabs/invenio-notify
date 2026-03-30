"""Constants for the Invenio-Notify module."""

#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

# Notification types
TYPE_REVIEW = 'coar-notify:ReviewAction'
TYPE_ENDORSEMENT = 'coar-notify:EndorsementAction'
TYPE_TENTATIVE_ACCEPT = 'TentativeAccept'
TYPE_REJECT = 'Reject'
TYPE_TENTATIVE_REJECT = 'TentativeReject'
""" List of supported notification types that can be processed by the notify  """

# Workflow status constants
WORKFLOW_STATUS_REQUEST_ENDORSEMENT = 'request_endorsement'
WORKFLOW_STATUS_TENTATIVE_ACCEPT = 'tentative_accept'
WORKFLOW_STATUS_TENTATIVE_REJECT = 'tentative_reject'
WORKFLOW_STATUS_ANNOUNCE_REVIEW = 'announce_review'
WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT = 'announce_endorsement'
WORKFLOW_STATUS_REJECT = 'reject'
WORKFLOW_STATUS_AVAILABLE = 'available' # This is not COAR standard, used internally.


STATUS_NOT_ACCEPTED = 422
STATUS_BAD_REQUEST = 400
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_SERVER_ERROR = 500

KEY_INBOX_REVIEW_URL = 'ietf:cite-as'

# Feature toggle configuration keys
NOTIFY_PCI_ENDORSEMENT = 'NOTIFY_PCI_ENDORSEMENT'
NOTIFY_PCI_ANNOUNCEMENT_OF_ENDORSEMENT = 'NOTIFY_PCI_ANNOUNCEMENT_OF_ENDORSEMENT'
