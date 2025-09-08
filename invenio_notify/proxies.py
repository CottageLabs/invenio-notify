"""Helper proxies to the state object."""

from typing import TYPE_CHECKING

from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from invenio_notify.services import (
        NotifyInboxService,
        ActorService,
        EndorsementAdminService,
        EndorsementRequestService,
        EndorsementReplyService,
    )

current_notify = LocalProxy(lambda: current_app.extensions["invenio-notify"])

current_actor_service: 'ActorService' = LocalProxy(  # type:ignore[assignment]
    lambda: current_notify.actor_service
)

current_endorsement_service: 'EndorsementAdminService' = LocalProxy( # type:ignore[assignment]
    lambda: current_notify.endorsement_service
)

current_inbox_service: 'NotifyInboxService' = LocalProxy( # type:ignore[assignment]
    lambda: current_notify.notify_inbox_service
)

current_endorsement_request_service: 'EndorsementRequestService' = LocalProxy( # type:ignore[assignment]
    lambda: current_notify.endorsement_request_service
)

current_endorsement_reply_service: 'EndorsementReplyService' = LocalProxy( # type:ignore[assignment]
    lambda: current_notify.endorsement_reply_service
)


