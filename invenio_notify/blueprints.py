#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from flask import Blueprint

from invenio_notify import feature_toggle

blueprint = Blueprint(
    "notify",
    __name__,
    template_folder="templates",
)


def create_inbox_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].inbox_admin_resource.as_blueprint()


def create_actor_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].actor_admin_resource.as_blueprint()


@feature_toggle.pci_endorsement_blueprint_enable
def create_inbox_api_resource_bp(app):
    return app.extensions["invenio-notify"].inbox_api_resource.as_blueprint()


def create_endorsement_request_resource_api_bp(app):
    return app.extensions["invenio-notify"].endorsement_request_resource.as_blueprint()


def create_endorsement_request_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].endorsement_request_admin_resource.as_blueprint()


def create_endorsement_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].endorsement_admin_resource.as_blueprint()
