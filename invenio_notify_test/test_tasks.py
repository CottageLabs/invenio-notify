import json
import pytest
from datetime import datetime
from invenio_access.permissions import system_identity
from invenio_files_rest.models import Location
from invenio_rdm_records.proxies import current_rdm_records
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from conftest import create_notification_data
from invenio_notify.records.models import NotifyInboxModel, EndorsementMetadataModel
from invenio_notify.tasks import inbox_processing, mark_as_processed


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    # vocabulary_service.create(
    #     system_identity,
    #     {
    #         "id": "dataset",
    #         "icon": "table",
    #         "props": {
    #             "csl": "dataset",
    #             "datacite_general": "Dataset",
    #             "datacite_type": "",
    #             "openaire_resourceType": "21",
    #             "openaire_type": "dataset",
    #             "eurepo": "info:eu-repo/semantics/other",
    #             "schema.org": "https://schema.org/Dataset",
    #             "subtype": "",
    #             "type": "dataset",
    #             "marc21_type": "dataset",
    #             "marc21_subtype": "",
    #         },
    #         "title": {"en": "Dataset"},
    #         "tags": ["depositable", "linkable"],
    #         "type": "resourcetypes",
    #     },
    # )
    #
    # vocabulary_service.create(
    #     system_identity,
    #     {  # create base resource type
    #         "id": "image",
    #         "props": {
    #             "csl": "figure",
    #             "datacite_general": "Image",
    #             "datacite_type": "",
    #             "openaire_resourceType": "25",
    #             "openaire_type": "dataset",
    #             "eurepo": "info:eu-repo/semantics/other",
    #             "schema.org": "https://schema.org/ImageObject",
    #             "subtype": "",
    #             "type": "image",
    #             "marc21_type": "image",
    #             "marc21_subtype": "",
    #         },
    #         "icon": "chart bar outline",
    #         "title": {"en": "Image"},
    #         "tags": ["depositable", "linkable"],
    #         "type": "resourcetypes",
    #     },
    # )
    #
    # vocabulary_service.create(
    #     system_identity,
    #     {  # create base resource type
    #         "id": "software",
    #         "props": {
    #             "csl": "figure",
    #             "datacite_general": "Software",
    #             "datacite_type": "",
    #             "openaire_resourceType": "0029",
    #             "openaire_type": "software",
    #             "eurepo": "info:eu-repo/semantics/other",
    #             "schema.org": "https://schema.org/SoftwareSourceCode",
    #             "subtype": "",
    #             "type": "image",
    #             "marc21_type": "software",
    #             "marc21_subtype": "",
    #         },
    #         "icon": "code",
    #         "title": {"en": "Software"},
    #         "tags": ["depositable", "linkable"],
    #         "type": "resourcetypes",
    #     },
    # )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photo",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photo",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "photo",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


def test_mark_as_processed(db, superuser_identity):
    """Test the mark_as_processed function."""
    # Create a test inbox record
    inbox = NotifyInboxModel.create({'raw': 'test', 'record_id': 'r1', 'user_id': superuser_identity.id})

    # Initially, process_date should be None
    assert inbox.process_date is None

    # Mark as processed
    mark_as_processed(inbox, "Test comment")

    inbox = NotifyInboxModel.query.get(inbox.id)
    assert inbox.process_date is not None
    assert isinstance(inbox.process_date, datetime)


def test_inbox_processing_success(db, create_rdm_record, superuser_identity, minimal_record, resource_type_v):
    """Test successful inbox processing that creates an endorsement."""

    loc = Location(name='local', uri='tmpxxx', default=True)
    db.session.add(loc)
    db.session.commit()

    draft = current_rdm_records.records_service.create(superuser_identity, minimal_record)
    record = current_rdm_records.records_service.publish(superuser_identity, draft.id, )

    recid = create_rdm_record['id']

    notification_data = create_notification_data(recid)

    # Create inbox record with real notification data
    inbox = NotifyInboxModel.create({
        'raw': json.dumps(notification_data),
        'record_id': recid,
        'user_id': superuser_identity.id,
    })

    # Verify no endorsements exist before processing
    assert EndorsementMetadataModel.query.count() == 0

    # Run the processing task
    inbox_processing()

    # Refresh the inbox record from DB
    updated_inbox = NotifyInboxModel.get(inbox.id)

    # Check that the inbox record was marked as processed
    assert updated_inbox.process_date is not None

    # Verify an endorsement was created
    endorsements = EndorsementMetadataModel.query.all()
    assert len(endorsements) == 1

    # Verify the endorsement has the correct data
    endorsement = endorsements[0]
    assert endorsement.record_id == create_rdm_record.id
    assert endorsement.user_id == 1
    assert endorsement.inbox_id == inbox.id
    assert endorsement.review_type == 'endorsement'


def test_inbox_processing_record_not_found(db, superuser_identity):
    """Test inbox processing when the record is not found."""

    recid = 'r1'

    notification_data = create_notification_data(recid)

    # Create inbox record with notification pointing to non-existent record
    inbox = NotifyInboxModel.create({
        'raw': json.dumps(notification_data),
        'record_id': recid,
        'user_id': superuser_identity.id,
    })

    # Verify no endorsements exist before processing
    assert EndorsementMetadataModel.query.count() == 0

    # Run the processing task
    inbox_processing()

    # Refresh the inbox record from DB
    updated_inbox = NotifyInboxModel.get(inbox.id)

    # Check that the inbox record was marked as processed
    assert updated_inbox.process_date is not None

    # Verify no endorsement was created
    assert EndorsementMetadataModel.query.count() == 0
