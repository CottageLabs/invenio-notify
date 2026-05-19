#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.
from invenio_base import invenio_url_for
from invenio_drafts_resources.services.records.config import is_record
from invenio_rdm_records.services.schemas import RDMRecordSchema

from invenio_rdm_records.records import RDMRecord
from invenio_records.dumpers import SearchDumper
from invenio_records_resources.services import RecordEndpointLink
from marshmallow import fields
from marshmallow_utils.fields import NestedAttribute

from invenio_notify.records.dumpers import EndorsementsDumperExt, NotifyDumperExt
from invenio_notify.records.models import ActorModel
from invenio_notify.records.systemfields import NotifyField, EndorsementsField
from invenio_notify.services.schemas import NotifySchema, EndorsementSchema
from invenio_rdm_records.services import RDMRecordServiceConfig

from invenio_notify.notifications import builders


from invenio_notify import config, cli, feature_toggle, constants
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

        # Signposting
        sp = app.config.get("APP_RDM_RECORD_LANDING_PAGE_EXT_SIGNPOSTING_CONTRIBUTIONS")
        if sp:
            if notify_signposts not in sp:
                sp.append(notify_signposts)

        # sidebar templates for detail page
        endorsement_sidebar = app.config.get(constants.NOTIFY_ENDORSEMENT_SIDEBAR_TEMPLATE)
        endorsement_request_sidebar = app.config.get(constants.NOTIFY_ENDORSEMENT_REQUEST_SIDEBAR_TEMPLATE)
        sidebars = app.config.get("APP_RDM_DETAIL_SIDE_BAR_TEMPLATES")
        if endorsement_sidebar not in sidebars:
            sidebars.append(endorsement_sidebar)
        if endorsement_request_sidebar not in sidebars:
            sidebars.append(endorsement_request_sidebar)

        # notification builders
        nbs = app.config.get("NOTIFICATIONS_BUILDERS")
        if builders.NewEndorsementNotificationBuilder.type not in nbs:
            nbs[builders.NewEndorsementNotificationBuilder.type] = builders.NewEndorsementNotificationBuilder
        if builders.EndorsementUpdateNotificationBuilder.type not in nbs:
            nbs[builders.EndorsementUpdateNotificationBuilder.type] = builders.EndorsementUpdateNotificationBuilder

        if app.config.get("NOTIFY_USE_RDM_RECORD_EXTENSION", True):
            app.config["RDM_RECORD_CLS"] = NotifyEnabledRDMRecord

        if app.config.get("NOTIFY_USE_RDM_RECORD_SCHEMA_EXTENSION", True):
            app.config["RDM_RECORD_SCHEMA"] = NotifyEnabledRDMRecordSchema

        # Globals required by jinja2
        app.jinja_env.filters["notify_enable_endorsement_request_section"] = enable_endorsement_request_sidebar

        # Links on RDMRecordServiceConfig
        # RDMrecordServiceConfig can't be configured away, so we can rely on this specific class being available
        RDMRecordServiceConfig.links_item.update({
            # Endorsements Requests
            "endorsement_request": RecordEndpointLink("endorsement_request.send", when=is_record_owner),
            "endorsement_request_actors": RecordEndpointLink("endorsement_request.list_actors", when=is_record_owner)
        })


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

class NotifyRDMRecordMixin:
    """
    Add this class to any extension of RDMRecord to add the Notify capabilities
    """
    endorsements = EndorsementsField()
    notify = NotifyField()

    # FIXME: there doesn't seem to be a way to extend the dumper on a module, so we
    # are creating and binding a new dumper based on the RDMRecords settings, so we
    # don't lose anything from the core implementation
    dumper = SearchDumper(extensions=RDMRecord.dumper._extensions + [
        EndorsementsDumperExt("endorsements"),
        NotifyDumperExt("notify")
    ])


class NotifyEnabledRDMRecord(NotifyRDMRecordMixin, RDMRecord):
    """
    A class which we can use to enable RDMRecord on an otherwise vanilla InvenioRDM or
    one which doesn't otherwise extend RDMRecord.
    """
    pass

class NotifyRDMRecordSchemaMixin:
    endorsements = fields.List(fields.Nested(EndorsementSchema), dump_only=True)
    notify = NestedAttribute(NotifySchema, dump_only=True)


class NotifyEnabledRDMRecordSchema(RDMRecordSchema, NotifyRDMRecordSchemaMixin):
    pass


def is_record_owner(record, ctx):
    from flask import g
    return (is_record(record, ctx)
            and hasattr(g, "identity") and hasattr(g.identity, "id")
            and record.parent.access.owner.owner_id == g.identity.id)

def enable_endorsement_request_sidebar(record):
    # Check if endorsement requests section should be displayed
    # Only check for logged in users, record owners, and if the feature is enabled
    from flask import current_app as app
    from flask_login import current_user
    enable_endorsement_request_section = False
    if app.config.get(constants.NOTIFY_ENDORSEMENT_RECEIVE) and app.config.get(constants.NOTIFY_ENDORSEMENT_REQUEST):
        if current_user.is_authenticated:
            # Check if user is the record owner
            if record._record.parent.access.owned_by.owner_id == current_user.id:
                try:
                    enable_endorsement_request_section = ActorModel.has_available_actors(record._record.id)
                except Exception:
                    pass
    return enable_endorsement_request_section

def notify_signposts(app, record):
    if app.config.get(constants.NOTIFY_ENDORSEMENT_RECEIVE, False):
        inbox = invenio_url_for("inbox_api.receive_notification")
        return f' , <{inbox}> ; rel="http://www.w3.org/ns/ldp#inbox"'
    return None