"""Test get record id from notification using a doi."""

import pytest
from unittest.mock import patch
from invenio_rdm_records.proxies import current_rdm_records

from invenio_notify.services.service.inbox_service import get_record_id_from_notification


@pytest.fixture()
def mock_public_doi():
    def public_doi(self, *args, **kwargs):
        # success
        pass

    patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        + "DataCiteRESTClient.public_doi",
        public_doi,
    )


def test_resolve_record_from_doi(running_app, search_clear, location,
                                 resource_type_v, minimal_record, mock_public_doi):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    minimal_record["pids"] = {}
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)
    published_doi = record["pids"]["doi"]
    parent_doi = record["parent"]["pids"]["doi"]

    assert record._data['id'] == get_record_id_from_notification(
        {'context': {'id': published_doi["identifier"]}})
    assert record._data['id'] == get_record_id_from_notification(
        {'context': {'id': 'https://doi.org/' + published_doi["identifier"]}})
    assert record._data['id'] == get_record_id_from_notification(
        {'context': {'id': parent_doi["identifier"]}})  # concept doi resolves to latest version
