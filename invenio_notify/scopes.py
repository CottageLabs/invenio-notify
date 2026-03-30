#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from invenio_i18n import lazy_gettext as _

from invenio_oauth2server.models import Scope

inbox_scope = Scope(
    id_="notify:inbox",
    group="notify",
    help_text=_("Allow sending notification to the inbox."),
    internal=True
)
