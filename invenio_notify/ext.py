from invenio_notify import config, cli, feature_toggle
from invenio_notify.blueprints import blueprint
from invenio_notify.resources import (
    InboxAdminResourceConfig,
    ActorAdminResourceConfig,
    InboxApiResourceConfig,
    EndorsementRequestResourceConfig,
    EndorsementRequestAdminResourceConfig,
    EndorsementAdminResourceConfig,
    InboxAdminResource,
    ActorAdminResource,
    InboxApiResource,
    EndorsementRequestResource,
    EndorsementRequestAdminResource,
    EndorsementAdminResource,
)
from invenio_notify.services import (
    EndorsementReplyServiceConfig,
    EndorsementRequestServiceConfig,
    EndorsementAdminServiceConfig,
    NotifyInboxServiceConfig,
    ActorMapServiceConfig,
    ActorServiceConfig,
    EndorsementReplyService,
    EndorsementRequestService,
    EndorsementAdminService,
    NotifyInboxService,
    ActorMapService,
    ActorService,
)


class InvenioNotify:

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

            # set logger level to debug
            log_level = app.config.get('NOTIFY_LOG_LEVEL')
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

        from invenio_notify.notifications import builders
        app.config['NOTIFICATIONS_BUILDERS'] = app.config.get('NOTIFICATIONS_BUILDERS', {}) | {
            b.type: b for b in [builders.NewEndorsementNotificationBuilder,
                                builders.EndorsementUpdateNotificationBuilder]
        }

    def init_services(self, app):
        """Initialize the services for notifications."""
        self.notify_inbox_service = NotifyInboxService(config=NotifyInboxServiceConfig)
        self.endorsement_service = EndorsementAdminService(config=EndorsementAdminServiceConfig)
        self.actor_map_service = ActorMapService(config=ActorMapServiceConfig)
        self.actor_service = ActorService(config=ActorServiceConfig)
        self.endorsement_request_service = EndorsementRequestService(config=EndorsementRequestServiceConfig)
        self.endorsement_reply_service = EndorsementReplyService(config=EndorsementReplyServiceConfig)

    def init_resources(self, app):
        """Initialize the resources for notifications."""

        if feature_toggle.is_pci_endorsement_enabled(app):
            self.inbox_api_resource = InboxApiResource(
                service=self.notify_inbox_service,
                config=InboxApiResourceConfig,
            )


        self.inbox_admin_resource = InboxAdminResource(
            service=self.notify_inbox_service,
            config=InboxAdminResourceConfig,
        )
        self.actor_admin_resource = ActorAdminResource(
            service=self.actor_service,
            config=ActorAdminResourceConfig,
        )
        self.endorsement_admin_resource = EndorsementAdminResource(
            service=self.endorsement_service,
            config=EndorsementAdminResourceConfig,
        )

        self.endorsement_request_resource = EndorsementRequestResource(
            config=EndorsementRequestResourceConfig.build(app),
        )
        self.endorsement_request_admin_resource = EndorsementRequestAdminResource(
            service=self.endorsement_request_service,
            config=EndorsementRequestAdminResourceConfig,
        )
