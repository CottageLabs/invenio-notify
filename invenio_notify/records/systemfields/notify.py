#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

"""Cached transient field for record notifications."""
from invenio_records.systemfields import SystemField
from invenio_search.proxies import current_search_client
from invenio_search.utils import build_alias_name

from invenio_notify.proxies import current_endorsement_service


def _get_record_notifications(record):
    """Get the record's notifications from either record or search index."""
    try:
        # note: this field is dumped into the record's data before indexing
        #       by the search dumper extension "NotifyDumperExt"
        res = current_search_client.get(
            index=build_alias_name(record.index._name),
            id=record.id,
            params={"_source_includes": "notify"},
        )
        notifications = res["_source"]["notify"]
    except Exception:
        notifications = None

    return notifications or current_endorsement_service.get_notify_info(record.parent.id)


class NotifyField(SystemField):
    """Field for lazy fetching and caching (but not storing) of record notifications."""

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the notification information."""
        if record is None:
            # returns the field itself.
            return self

        if not record.get("notify"):
            record["notify"] = _get_record_notifications(record)

        return record["notify"]

    def pre_commit(self, record, **kwargs):
        """Ensure that the notifications stay transient."""
        record.pop("notify", None)

    def pre_dump(self, record, data, **kwargs):
        """Do nothing in particular before a record is dumped."""
        # note: there's no pre/post-dump work being done in the system field because
        #       we only want the notifications to be dumped into the search engine, which is
        #       done over at the "NotifyDumperExt" search dumper extension
        #       putting that logic here would require more research into when a
        #       system field's `pre_dump()` is called
        pass
