from invenio_notify import config, cli
from invenio_notify.blueprints import blueprint
from invenio_notify.resources.config import (
    NotifyInboxResourceConfig,
    ReviewerResourceConfig,
    InboxApiResourceConfig,
)
from invenio_notify.resources.resource import (
    NotifyInboxResource,
    ReviewerResource,
    InboxApiResource,
)
from invenio_notify.services.config import (
    EndorsementReplyServiceConfig,
    EndorsementRequestServiceConfig,
    EndorsementServiceConfig,
    NotifyInboxServiceConfig,
    ReviewerMapServiceConfig,
    ReviewerServiceConfig,
)
from invenio_notify.services.service import (
    EndorsementReplyService,
    EndorsementRequestService,
    EndorsementService,
    NotifyInboxService,
    ReviewerMapService,
    ReviewerService,
)


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

        from invenio_notify.notifications.builders import NewEndorsementNotificationBuilder
        app.config['NOTIFICATIONS_BUILDERS'] = app.config.get('NOTIFICATIONS_BUILDERS', {}) | {
            b.type: b for b in [NewEndorsementNotificationBuilder, ]
        }

    def init_services(self, app):
        """Initialize the services for notifications."""
        self.notify_inbox_service = NotifyInboxService(config=NotifyInboxServiceConfig)
        self.endorsement_service = EndorsementService(config=EndorsementServiceConfig)
        self.reviewer_map_service = ReviewerMapService(config=ReviewerMapServiceConfig)
        self.reviewer_service = ReviewerService(config=ReviewerServiceConfig)
        self.endorsement_request_service = EndorsementRequestService(config=EndorsementRequestServiceConfig)
        self.endorsement_reply_service = EndorsementReplyService(config=EndorsementReplyServiceConfig)

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
        self.inbox_api_resource = InboxApiResource(
            service=self.notify_inbox_service,
            config=InboxApiResourceConfig,
        )
