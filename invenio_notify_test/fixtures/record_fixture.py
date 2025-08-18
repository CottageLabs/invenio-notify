from invenio_rdm_records.records import RDMParent, RDMRecord


def prepare_test_rdm_record(db, record_data):
    parent = RDMParent.create({})
    record = RDMRecord.create(record_data, parent=parent)
    db.session.commit()
    return record