from invenio_notify import config
from invenio_notify.blueprints import blueprint
from invenio_notify.resources.config import NotifyInboxResourceConfig
from invenio_notify.resources.resource import NotifyInboxResource
from invenio_notify.services.conf import NotifyInboxServiceConfig
from invenio_notify.services.service import NotifyInboxService


class InvenioNotify:

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.init_config(app)
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-notify"] = self
        app.register_blueprint(blueprint)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("NOTIFY_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Initialize the services for notifications."""
        self.notify_inbox_service = NotifyInboxService(config=NotifyInboxServiceConfig)

    def init_resources(self, app):
        """Initialize the resources for notifications."""
        self.notify_inbox_resource = NotifyInboxResource(
            service=self.notify_inbox_service,
            config=NotifyInboxResourceConfig,
        )
