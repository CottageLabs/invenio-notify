#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.
from invenio_drafts_resources.services.records.config import is_record
from invenio_records_resources.services import RecordEndpointLink
from marshmallow import fields
from marshmallow_utils.fields import NestedAttribute

from invenio_notify.records.dumpers import EndorsementsDumperExt, NotifyDumperExt
from invenio_notify.records.systemfields import NotifyField, EndorsementsField
from invenio_notify.services.schemas import NotifySchema, EndorsementSchema
from invenio_rdm_records.services import RDMRecordService, RDMRecordServiceConfig

from invenio_rdm_records.proxies import current_rdm_records_service

from invenio_records_resources.services.records.facets import TermsFacet
from invenio_i18n import lazy_gettext as _

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
        # pull in all the configs prefixed with NOTIFY_
        for k in dir(config):
            if k.startswith("NOTIFY_"):
                app.config.setdefault(k, getattr(config, k))

        # now add our operational parameters to the various objects
        svc: RDMRecordService = current_rdm_records_service

        # Links on RDMRecordServiceConfig
        cfg: RDMRecordServiceConfig = svc.config
        svc.config.links_item.update({
            # Endorsements Requests
            "endorsement_request": RecordEndpointLink("endorsement_request.send", when=is_record_owner),
            "endorsement_request_actors": RecordEndpointLink("endorsement_request.list_actors", when=is_record_owner)
        })

        # Custom dumpers on RDMRecord SearchDumper
        # Note that there's no API for adding extensions, so we are directly accessing a private
        # variable
        cfg.record_cls.dumper._extensions.append(EndorsementsDumperExt("endorsements"))
        cfg.record_cls.dumper._extensions.append(NotifyDumperExt("notify"))

        # Custom system fields on RDMRecord
        cfg.record_cls.endorsements = EndorsementsField()
        cfg.record_cls.notify = NotifyField()

        # Custom schemas on RDMRecordSchema
        cfg.schema.endorsements = fields.List(fields.Nested(EndorsementSchema), dump_only=True)
        cfg.schema.notify = NestedAttribute(NotifySchema, dump_only=True)


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

def finalize_app(app):
    """Finalise the app."""
    pass

def is_record_owner(record, ctx):
    from flask import g
    return (is_record(record, ctx)
            and hasattr(g, "identity") and hasattr(g.identity, "id")
            and record.parent.access.owner.owner_id == g.identity.id)