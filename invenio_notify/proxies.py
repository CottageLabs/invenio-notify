"""Helper proxies to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

current_notify = LocalProxy(lambda: current_app.extensions["invenio-notify"])
"""Helper proxy to get the current Notify extension."""

current_reviewer_service = LocalProxy(
    lambda: current_app.extensions["invenio-notify"].reviewer_service
)
"""Helper proxy to get the current Reviewer service extension."""


current_endorsement_service = LocalProxy(
    lambda: current_app.extensions["invenio-notify"].endorsement_service
)