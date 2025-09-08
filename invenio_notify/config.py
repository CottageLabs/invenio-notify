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


