#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from invenio_access import action_factory
from invenio_access.permissions import Permission
from invenio_records_permissions.generators import Generator

coarnotify_action = action_factory("coarnotify")
coarnotify_permission = Permission(coarnotify_action)


class Coarnotify(Generator):

    def __init__(self):
        """Constructor."""
        super(Coarnotify, self).__init__()

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [coarnotify_action]
