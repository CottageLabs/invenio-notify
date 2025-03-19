from invenio_i18n import lazy_gettext as _

NOTIFY_SEARCH = {
    "facets": [],
    "sort": [
        "raw",
        "raw",
    ],
}

NOTIFY_SORT_OPTIONS = {
    "raw": dict(
        title=_("Raw"),
        fields=["raw"],
    ),
    # "url_path": dict(
    #     title=_("URL path"),
    #     fields=["url_path"],
    # ),
    # "start_datetime": dict(
    #     title=_("Start DateTime"),
    #     fields=["start_datetime"],
    # ),
    # "end_datetime": dict(
    #     title=_("End DateTime"),
    #     fields=["end_datetime"],
    # ),
    # "active": dict(
    #     title=_("Active"),
    #     fields=["active"],
    # ),
}


