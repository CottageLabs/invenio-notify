#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from invenio_rdm_records.records import RDMParent

from invenio_notify.ext import NotifyEnabledRDMRecord


def prepare_test_rdm_record(db, record_data):
    parent = RDMParent.create({})
    record = NotifyEnabledRDMRecord.create(record_data, parent=parent)
    db.session.commit()
    return record