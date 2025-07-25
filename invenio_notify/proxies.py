"""Helper proxies to the state object."""

from typing import TYPE_CHECKING

from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from invenio_notify.services.service import (
        NotifyInboxService,
        ReviewerService,
        EndorsementService,
        EndorsementRequestService,
        EndorsementReplyService,
    )

current_notify = LocalProxy(lambda: current_app.extensions["invenio-notify"])

current_reviewer_service: 'ReviewerService' = LocalProxy(  # type:ignore[assignment]
    lambda: current_notify.reviewer_service
)

current_endorsement_service: 'EndorsementService' = LocalProxy( # type:ignore[assignment]
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


