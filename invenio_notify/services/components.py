"""Components."""

from flask import current_app
from invenio_access.permissions import system_identity, system_process
from invenio_db import db
from invenio_i18n import lazy_gettext as _
from invenio_oaiserver.models import OAISet
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.services.records.components import (
    MetadataComponent,
    RelationsComponent,
    ServiceComponent,
)
from marshmallow.exceptions import ValidationError


class FieldComponent(ServiceComponent):

    def create(self, identity, data=None, record=None, **kwargs):

        super().create(identity, **kwargs)


        for k, v in data.items():
            setattr(record.model, k, v)


        # breakpoint()

    # def read(self, identity, **kwargs):
    #     super().read(identity, **kwargs)
    #     breakpoint()
    #
    # def update(self, identity, **kwargs):
    #     super().update(identity, **kwargs)
    #     breakpoint()
    #
    # def delete(self, identity, **kwargs):
    #     super().delete(identity, **kwargs)
    #     breakpoint()
    #
    # def search(self, identity, search, params, **kwargs):
    #     breakpoint()
    #     return super().search(identity, search, params, **kwargs)
    #

DefaultEndorsementComponents = [
    MetadataComponent,
    FieldComponent,
]
