#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.
from invenio_drafts_resources.services import RecordServiceConfig
from invenio_drafts_resources.records.api import Record
from invenio_records_resources.services import Service, ServiceConfig, RecordService
from invenio_records_resources.services.records.results import RecordItem

from invenio_rdm_records import InvenioRDMRecords

from invenio_rdm_records.records.models import RDMRecordMetadata

from invenio_rdm_records.services.config import RDMSearchOptions

from invenio_rdm_records.services.schemas import RDMRecordSchema

from invenio_rdm_records.records import RDMRecord

from invenio_rdm_records.services import RDMRecordService, RDMRecordServiceConfig

CLASSES = [
    RDMRecordService,
    RDMRecordServiceConfig,
    RDMRecord,
    RDMRecordSchema,
    RDMSearchOptions,
    RDMRecordMetadata,
    InvenioRDMRecords,

    Service,
    ServiceConfig,

    RecordService,
    RecordServiceConfig,
    RecordItem,
    Record,
]
