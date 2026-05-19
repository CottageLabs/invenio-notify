"""Components."""

#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from invenio_records_resources.services.records.components import (
    MetadataComponent,
    ServiceComponent,
)


class FieldComponent(ServiceComponent):

    def create(self, identity, data=None, record=None, **kwargs):

        super().create(identity, **kwargs)


        for k, v in data.items():
            setattr(record.model, k, v)


DefaultEndorsementComponents = [
    MetadataComponent,
    FieldComponent,
]
