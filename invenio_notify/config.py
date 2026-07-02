#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.
import regex
from invenio_i18n import lazy_gettext as _

from invenio_notify.constants import WORKFLOW_STATUS_REQUEST_ENDORSEMENT, WORKFLOW_STATUS_TENTATIVE_ACCEPT, \
    WORKFLOW_STATUS_TENTATIVE_REJECT, WORKFLOW_STATUS_REJECT, WORKFLOW_STATUS_AVAILABLE
from invenio_notify.workflows.endorsement import EndorsementWorkflow

###############################
## General Notify configuration
## NOTIFY_ prefixed

NOTIFY_ORIGIN_ID = 'https://127.0.0.1:5000/'
"""
This is the URL which is used in the `origin.id` field of all outgoing notifications.  
See https://coar-notify.net/specification/1.0.1/

This is distinct from the `origin.inbox` which will be dynamically generated for your instance
"""

NOTIFY_USE_RDM_RECORD_EXTENSION = True
"""
Should the notify module patch in its own RDMRecord class?  If set to true, this will override
RDMRecord with NotifyEnabledRDMRecord.  If set to false you MUST specify your own implementation
of RDMRecord using the RDM_RECORD_CLS config variable, and that implementation MUST include 
the Notify extension, which can be done by extending the NotifyRDMRecordMixin class as well as the RDMRecord class.
See the documentation for more details.
"""

NOTIFY_USE_RDM_RECORD_SCHEMA_EXTENSION = True
"""
Should the notify module patch in its own RDMRecordSchema class?  If set to true, this will override
RDMRecordSchema with NotifyEnabledRDMRecordSchema.  If set to false you MUST specify your own implementation
of RDMRecordSchema using the RDM_RECORD_SCHEMA config variable, and that implementation MUST include 
the Notify extension, which can be done by extending the NotifyRDMRecordSchemaMixin class as well as the RDMRecordSchema class.
See the documentation for more details.
"""

NOTIFY_RECORD_ID_URL_REGEX = regex.compile(r'/records/(.*?)$')
NOTIFY_RECORD_ID_ALT_URL_REGEX = regex.compile(r'/records/([^/]+)/?')
"""
Regexes which can extract Record IDs from the URL space.  You may need to override these if your Invenio
instance has customised the URL space
"""

NOTIFY_WORKFLOWS = [EndorsementWorkflow]
"""
A list of the workflow engines to use to process the notifications that arrive in the inbox.
"""

##############################
## Endorsement Workflow Config
## NOTIFY_ENDORSEMENT_ prefixed

NOTIFY_ENDORSEMENT_RECEIVE = True
"""
Enables the ability to receive endorsement and review notifications for actors using the
Endorsement workflow.  If set to true, while NOTIFY_ENDORSEMENT_REQUEST is set to False
your repository will support only this workflow: https://coar-notify.net/catalogue/workflows/pci-sciety/
"""

NOTIFY_ENDORSEMENT_REQUEST = True
"""
Enables the ability to send endorsement requests, and thus enables the full Endorsement workflow
as documented here https://coar-notify.net/catalogue/workflows/repository-pci/

For this to work NOTIFY_ENDORSEMENT_RECEIVE MUST be set to True.
"""

NOTIFY_ENDORSEMENT_STATUS_LABELS = {
    WORKFLOW_STATUS_TENTATIVE_ACCEPT: 'In progress',
    WORKFLOW_STATUS_REJECT: {'label': 'Rejected', 'labelClass': 'red'},
    WORKFLOW_STATUS_TENTATIVE_REJECT: {'label': 'Not endorsed in current form', 'labelClass': 'orange'},
    WORKFLOW_STATUS_REQUEST_ENDORSEMENT: 'Pending',
    WORKFLOW_STATUS_AVAILABLE: {'label': 'Available', 'labelClass': 'green'},
}
"""Configuration for endorsement status labels.

This configuration defines how endorsement statuses are displayed in the UI.
Each status can be configured in two ways:

1. String format (simple):
   - The value is a string representing the display label

2. Dictionary format (advanced):
   - 'label': The display text for the status
   - 'labelClass': CSS class for styling (e.g., 'red', 'green', 'orange')  
   - 'labelTitle': Optional tooltip text shown on hover

Examples:
    NOTIFY_ENDORSEMENT_STATUS_LABELS = {
        # String format - simple label with default styling
        'pending': 'Awaiting Review',

        # Dictionary format - full control over appearance
        'approved': {
            'label': 'Approved',
            'labelClass': 'green',
            'labelTitle': 'This endorsement has been approved'
        },

        # Dictionary format - minimal (labelTitle is optional)
        'rejected': {
            'label': 'Rejected', 
            'labelClass': 'red'
        }
    }
"""


NOTIFY_ENDORSEMENT_AVAILABLE_ACTORS = [WORKFLOW_STATUS_TENTATIVE_REJECT, WORKFLOW_STATUS_AVAILABLE]
"""
Config variable for endorsement requests react component that determines
which workflow states mean that an actor is available to request an endorsement
from
"""

NOTIFY_ENDORSEMENT_SIDEBAR_TEMPLATE = "invenio_notify/records/details/side_bar/endorsements.html"
NOTIFY_ENDORSEMENT_REQUEST_SIDEBAR_TEMPLATE = "invenio_notify/records/details/side_bar/endorsement_request.html"

###########################################
## General admin configuration
## (You probably don't need to change this)

NOTIFY_INBOX_SEARCH = {
    "facets": [],
    "sort": [
        "id",
        "-id",
        "created",
        "-created",
        "updated",
        "-updated",
        "process_date",
        "-process_date",
        "record_id",
        "-record_id",
        "user_id",
        "-user_id",
    ],
}

NOTIFY_INBOX_SORT_OPTIONS = {
    "id": dict(
        title=_("ID (Ascending)"),
        fields=["id"],
    ),
    "-id": dict(
        title=_("ID (Descending)"),
        fields=["-id"],
    ),
    "created": dict(
        title=_("Created (Newest First)"),
        fields=["created"],
    ),
    "-created": dict(
        title=_("Created (Oldest First)"),
        fields=["-created"],
    ),
    "updated": dict(
        title=_("Updated (Newest First)"),
        fields=["updated"],
    ),
    "-updated": dict(
        title=_("Updated (Oldest First)"),
        fields=["-updated"],
    ),
    "process_date": dict(
        title=_("Process Date (Newest First)"),
        fields=["process_date"],
    ),
    "-process_date": dict(
        title=_("Process Date (Oldest First)"),
        fields=["-process_date"],
    ),
    "record_id": dict(
        title=_("Record ID (A-Z)"),
        fields=["record_id"],
    ),
    "-record_id": dict(
        title=_("Record ID (Z-A)"),
        fields=["-record_id"],
    ),
    "user_id": dict(
        title=_("User ID (Ascending)"),
        fields=["user_id"],
    ),
    "-user_id": dict(
        title=_("User ID (Descending)"),
        fields=["-user_id"],
    ),
}

NOTIFY_ACTOR_SEARCH = {
    "facets": [],
    "sort": [
        "id",
        "-id",
        "name",
        "-name",
        "created",
        "-created",
        "updated",
        "-updated",
        "actor_id",
        "-actor_id",
    ],
}

NOTIFY_ACTOR_SORT_OPTIONS = {
    "id": dict(
        title=_("ID (Ascending)"),
        fields=["id"],
    ),
    "-id": dict(
        title=_("ID (Descending)"),
        fields=["-id"],
    ),
    "name": dict(
        title=_("Name (A-Z)"),
        fields=["name"],
    ),
    "-name": dict(
        title=_("Name (Z-A)"),
        fields=["-name"],
    ),
    "created": dict(
        title=_("Created (Newest First)"),
        fields=["created"],
    ),
    "-created": dict(
        title=_("Created (Oldest First)"),
        fields=["-created"],
    ),
    "updated": dict(
        title=_("Updated (Newest First)"),
        fields=["updated"],
    ),
    "-updated": dict(
        title=_("Updated (Oldest First)"),
        fields=["-updated"],
    ),
    "actor_id": dict(
        title=_("Actor ID (A-Z)"),
        fields=["actor_id"],
    ),
    "-actor_id": dict(
        title=_("Actor ID (Z-A)"),
        fields=["-actor_id"],
    ),
}

NOTIFY_ENDORSEMENT_SEARCH = {
    "facets": [],
    "sort": [
        "id",
        "-id", 
        "record_id",
        "-record_id",
        "actor_id",
        "-actor_id",
        "actor_name",
        "-actor_name",
        "review_type",
        "-review_type",
        "created",
        "-created",
        "updated",
        "-updated",
    ],
}

NOTIFY_ENDORSEMENT_SORT_OPTIONS = {
    "id": dict(
        title=_("ID (Ascending)"),
        fields=["id"],
    ),
    "-id": dict(
        title=_("ID (Descending)"),
        fields=["-id"],
    ),
    "record_id": dict(
        title=_("Record ID (A-Z)"),
        fields=["record_id"],
    ),
    "-record_id": dict(
        title=_("Record ID (Z-A)"),
        fields=["-record_id"],
    ),
    "actor_id": dict(
        title=_("Actor ID (Ascending)"),
        fields=["actor_id"],
    ),
    "-actor_id": dict(
        title=_("Actor ID (Descending)"),
        fields=["-actor_id"],
    ),
    "actor_name": dict(
        title=_("Actor Name (A-Z)"),
        fields=["actor_name"],
    ),
    "-actor_name": dict(
        title=_("Actor Name (Z-A)"),
        fields=["-actor_name"],
    ),
    "review_type": dict(
        title=_("Review Type (A-Z)"),
        fields=["review_type"],
    ),
    "-review_type": dict(
        title=_("Review Type (Z-A)"),
        fields=["-review_type"],
    ),
    "created": dict(
        title=_("Created (Newest First)"),
        fields=["created"],
    ),
    "-created": dict(
        title=_("Created (Oldest First)"),
        fields=["-created"],
    ),
    "updated": dict(
        title=_("Updated (Newest First)"),
        fields=["updated"],
    ),
    "-updated": dict(
        title=_("Updated (Oldest First)"),
        fields=["-updated"],
    ),
}

NOTIFY_ENDORSEMENT_REQUEST_SEARCH = {
    "facets": [],
    "sort": [
        "id",
        "-id",
        "notification_id",
        "-notification_id",
        "record_id",
        "-record_id",
        "user_id",
        "-user_id",
        "actor_id",
        "-actor_id",
        "latest_status",
        "-latest_status",
        "created",
        "-created",
        "updated",
        "-updated",
    ],
}

NOTIFY_ENDORSEMENT_REQUEST_SORT_OPTIONS = {
    "id": dict(
        title=_("ID (Ascending)"),
        fields=["id"],
    ),
    "-id": dict(
        title=_("ID (Descending)"),
        fields=["-id"],
    ),
    "notification_id": dict(
        title=_("Notification ID (Ascending)"),
        fields=["notification_id"],
    ),
    "-notification_id": dict(
        title=_("Notification ID (Descending)"),
        fields=["-notification_id"],
    ),
    "record_id": dict(
        title=_("Record ID (A-Z)"),
        fields=["record_id"],
    ),
    "-record_id": dict(
        title=_("Record ID (Z-A)"),
        fields=["-record_id"],
    ),
    "user_id": dict(
        title=_("User ID (Ascending)"),
        fields=["user_id"],
    ),
    "-user_id": dict(
        title=_("User ID (Descending)"),
        fields=["-user_id"],
    ),
    "actor_id": dict(
        title=_("Actor ID (Ascending)"),
        fields=["actor_id"],
    ),
    "-actor_id": dict(
        title=_("Actor ID (Descending)"),
        fields=["-actor_id"],
    ),
    "latest_status": dict(
        title=_("Latest Status (A-Z)"),
        fields=["latest_status"],
    ),
    "-latest_status": dict(
        title=_("Latest Status (Z-A)"),
        fields=["-latest_status"],
    ),
    "created": dict(
        title=_("Created (Newest First)"),
        fields=["created"],
    ),
    "-created": dict(
        title=_("Created (Oldest First)"),
        fields=["-created"],
    ),
    "updated": dict(
        title=_("Updated (Newest First)"),
        fields=["updated"],
    ),
    "-updated": dict(
        title=_("Updated (Oldest First)"),
        fields=["-updated"],
    ),
}
