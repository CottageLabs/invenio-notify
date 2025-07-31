from flask import Blueprint

from invenio_notify import feature_toggle

blueprint = Blueprint(
    "notify",
    __name__,
    template_folder="templates",
)


def create_inbox_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].inbox_admin_resource.as_blueprint()


def create_reviewer_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].reviewer_admin_resource.as_blueprint()


@feature_toggle.phase_1_blueprint_enable
def create_inbox_api_resource_bp(app):
    return app.extensions["invenio-notify"].inbox_api_resource.as_blueprint()


def create_endorsement_request_resource_api_bp(app):
    return app.extensions["invenio-notify"].endorsement_request_resource.as_blueprint()


def create_endorsement_request_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].endorsement_request_admin_resource.as_blueprint()


def create_endorsement_admin_resource_api_bp(app):
    return app.extensions["invenio-notify"].endorsement_admin_resource.as_blueprint()
