"""Resources package."""

#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from .basic_db_resource import BasicDbResource
from .endorsement_request_admin_resource import EndorsementRequestAdminResource
from .endorsement_request_resource import EndorsementRequestResource
from .endorsement_admin_resource import EndorsementAdminResource
from .inbox_admin_resource import InboxAdminResource
from .inbox_api_resource import InboxApiResource
from .actor_admin_resource import ActorAdminResource

__all__ = [
    "BasicDbResource",
    "EndorsementRequestAdminResource", 
    "EndorsementRequestResource",
    "EndorsementAdminResource",
    "InboxAdminResource",
    "InboxApiResource",
    "ActorAdminResource",
]