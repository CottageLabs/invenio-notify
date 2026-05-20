#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from .config import (
    InboxAdminResourceConfig,
    ActorAdminResourceConfig,
    InboxApiResourceConfig,
    EndorsementRequestResourceConfig,
    EndorsementRequestAdminResourceConfig,
    EndorsementAdminResourceConfig,
)
from .resource import (
    NotifyResource,
    EndorsementRequestAdminResource,
    EndorsementRequestResource,
    EndorsementAdminResource,
    InboxAdminResource,
    InboxApiResource,
    ActorAdminResource,
)

__all__ = [
    # Resources
    "NotifyResource",
    "InboxAdminResource", 
    "ActorAdminResource",
    "InboxApiResource",
    "EndorsementRequestResource",
    "EndorsementRequestAdminResource",
    "EndorsementAdminResource",

    # Configs
    "InboxAdminResourceConfig",
    "ActorAdminResourceConfig", 
    "InboxApiResourceConfig",
    "EndorsementRequestResourceConfig",
    "EndorsementRequestAdminResourceConfig",
    "EndorsementAdminResourceConfig",
]