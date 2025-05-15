from invenio_notify import config, cli
from invenio_notify.blueprints import blueprint
from invenio_notify.resources.config import NotifyInboxResourceConfig, ReviewerResourceConfig
from invenio_notify.resources.resource import NotifyInboxResource, ReviewerResource
from invenio_notify.services.config import NotifyInboxServiceConfig, EndorsementServiceConfig, ReviewerMapServiceConfig, \
    ReviewerServiceConfig
from invenio_notify.services.service import NotifyInboxService, EndorsementService, ReviewerMapService, ReviewerService


class InvenioNotify:

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

            # set logger level to debug
            log_level = app.config.get('LOGGING_GENERAL_LEVEL')
            if log_level:
                app.logger.setLevel(log_level)

    def init_app(self, app):
        self.init_config(app)
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-notify"] = self
        app.register_blueprint(blueprint)

        app.cli.add_command(cli.notify)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("NOTIFY_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Initialize the services for notifications."""
        self.notify_inbox_service = NotifyInboxService(config=NotifyInboxServiceConfig)
        self.endorsement_service = EndorsementService(config=EndorsementServiceConfig.build(app))
        self.reviewer_map_service = ReviewerMapService(config=ReviewerMapServiceConfig)
        self.reviewer_service = ReviewerService(config=ReviewerServiceConfig)

    def init_resources(self, app):
        """Initialize the resources for notifications."""
        self.notify_inbox_resource = NotifyInboxResource(
            service=self.notify_inbox_service,
            config=NotifyInboxResourceConfig,
        )
        self.reviewer_resource = ReviewerResource(
            service=self.reviewer_service,
            config=ReviewerResourceConfig,
        )
