#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

"""Search dumpers for notify information."""

from invenio_records.dumpers import SearchDumperExt

from invenio_notify.proxies import current_endorsement_service


class NotifyDumperExt(SearchDumperExt):
    """Search dumper extension for Notify information. """

    def __init__(self, target_field):
        """Constructor.

        :param target_field: dot separated path where to dump the tokens.
        """
        super().__init__()
        self.key = target_field

    def dump(self, record, data):
        """Dump the notify information to the data dictionary."""
        if record.is_draft:
            return

        data[self.key] = current_endorsement_service.get_notify_info(record.parent.id)

    def load(self, data, record_cls):
        """Keep the notify information in the data dictionary.

        This is relevant for the "NotifyField" system field,
        which uses this entry in the record's data.
        """
        pass
