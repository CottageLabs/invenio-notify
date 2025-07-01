from flask import Blueprint, jsonify
from invenio_records_resources.services.errors import PermissionDeniedError

blueprint = Blueprint(
    "notify",
    __name__,
    template_folder="templates",
)

rest_blueprint = Blueprint(
    "notify_rest",
    __name__,
    url_prefix="/notify-rest",
    template_folder="templates",
)


@rest_blueprint.errorhandler(PermissionDeniedError)
def permission_denied_error(error):
    """Handle permission denier error on record views."""
    response = jsonify({"message": "Permission denied"})
    response.status_code = 403
    return response


def create_notify_inbox_resource_api_bp(app):
    return app.extensions["invenio-notify"].notify_inbox_resource.as_blueprint()


def create_reviewer_resource_api_bp(app):
    return app.extensions["invenio-notify"].reviewer_resource.as_blueprint()


def create_rest_blueprint(app):
    """Create rest blueprint with routes properly registered."""
    # Import here to ensure routes are registered after blueprint creation
    from invenio_notify.views import api_views  # noqa
    return rest_blueprint
