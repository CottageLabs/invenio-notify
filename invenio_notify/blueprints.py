from flask import Blueprint

blueprint = Blueprint(
    "notify",
    __name__,
    template_folder="templates",
)


def create_notify_inbox_resource_api_bp(app):
    return app.extensions["invenio-notify"].notify_inbox_resource.as_blueprint()


def create_reviewer_resource_api_bp(app):
    return app.extensions["invenio-notify"].reviewer_resource.as_blueprint()


def create_inbox_api_resource_bp(app):
    return app.extensions["invenio-notify"].inbox_api_resource.as_blueprint()


def create_endorsement_request_resource_api_bp(app):
    return app.extensions["invenio-notify"].endorsement_request_resource.as_blueprint()
