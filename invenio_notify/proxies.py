"""Helper proxies to the state object."""

from flask import current_app
from typing import TYPE_CHECKING
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from invenio_notify.services.service import NotifyInboxService, ReviewerService, EndorsementService

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


