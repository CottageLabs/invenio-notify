from invenio_i18n import lazy_gettext as _

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
        "recid",
        "-recid",
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
    "recid": dict(
        title=_("Record ID (A-Z)"),
        fields=["recid"],
    ),
    "-recid": dict(
        title=_("Record ID (Z-A)"),
        fields=["-recid"],
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

NOTIFY_REVIEWER_SEARCH = {
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

NOTIFY_REVIEWER_SORT_OPTIONS = {
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


