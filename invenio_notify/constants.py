"""Constants for the Invenio-Notify module."""

# Notification types
TYPE_REVIEW = 'coar-notify:ReviewAction'
TYPE_ENDORSEMENT = 'coar-notify:EndorsementAction'
REVIEW_TYPES = [TYPE_REVIEW, TYPE_ENDORSEMENT]



STATUS_NOT_ACCEPTED = 422
STATUS_BAD_REQUEST = 400
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404