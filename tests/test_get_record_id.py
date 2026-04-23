"""Test get_record_id_from_notification on NotifyInboxService."""

#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

import pytest
from unittest.mock import MagicMock, patch

from invenio_notify.errors import COARProcessFail
from invenio_notify.proxies import current_inbox_service


def _make_notification(context_id=None, object_id=None, nested_object_id=None):
    """Build a minimal NotifyPattern stub.

    Mirrors the three lookup paths in get_record_id_from_notification:
      1. context.id      -> pass context_id
      2. object.object.id -> pass nested_object_id
      3. object.id       -> pass object_id (without nested_object_id)
    """
    notification = MagicMock()

    # context
    if context_id is not None:
        notification.context = MagicMock()
        notification.context.id = context_id
    else:
        notification.context = None

    # object
    if object_id is not None or nested_object_id is not None:
        obj = MagicMock()
        obj.id = object_id
        if nested_object_id is not None:
            nested = MagicMock()
            nested.id = nested_object_id
            obj.object = nested
        else:
            # No nested object — fallback to obj.id
            del obj.object  # ensure hasattr(obj, 'object') is False
        notification.object = obj
    else:
        notification.object = None

    return notification


class TestGetRecordIdFromNotification:
    """Tests for NotifyInboxService.get_record_id_from_notification."""

    # ------------------------------------------------------------------
    # URL-based extraction (no DOI, no DB required)
    # ------------------------------------------------------------------

    def test_context_id_url(self, running_app):
        """Announce-type: record URL is in context.id."""
        notification = _make_notification(context_id="https://example.org/records/abc123")
        result = current_inbox_service.get_record_id_from_notification(notification)
        assert result == "abc123"

    def test_object_id_url(self, running_app):
        """Request-type fallback: record URL is in object.id."""
        notification = _make_notification(object_id="https://example.org/records/xyz789")
        result = current_inbox_service.get_record_id_from_notification(notification)
        assert result == "xyz789"

    def test_nested_object_id_url(self, running_app):
        """Reply-type: record URL is in object.object.id (NestedPatternObjectMixin)."""
        notification = _make_notification(nested_object_id="https://example.org/records/nested42")
        result = current_inbox_service.get_record_id_from_notification(notification)
        assert result == "nested42"

    def test_context_id_takes_priority_over_object_id(self, running_app):
        """context.id is preferred when both context and object are present."""
        notification = _make_notification(
            context_id="https://example.org/records/from-context",
            object_id="https://example.org/records/from-object",
        )
        result = current_inbox_service.get_record_id_from_notification(notification)
        assert result == "from-context"

    def test_no_record_url_raises(self, running_app):
        """Raises COARProcessFail when neither context nor object has an ID."""
        notification = _make_notification()
        with pytest.raises(COARProcessFail):
            current_inbox_service.get_record_id_from_notification(notification)

    # ------------------------------------------------------------------
    # DOI resolution (requires a published record and g.identity)
    # ------------------------------------------------------------------

    def test_resolve_record_from_doi(self, running_app, search_clear, location,
                                     resource_type_v, minimal_record):
        """DOI in context.id is resolved to the record's recid."""
        superuser_identity = running_app.superuser_identity
        from invenio_rdm_records.proxies import current_rdm_records
        service = current_rdm_records.records_service

        minimal_record["pids"] = {}
        draft = service.create(superuser_identity, minimal_record)
        record = service.publish(superuser_identity, draft.id)

        published_doi = record["pids"]["doi"]["identifier"]

        notification = _make_notification(context_id=published_doi)

        # get_record_id_from_notification uses flask.g.identity for DOI resolution
        import invenio_notify.services.service.inbox_service as svc_module
        with patch.object(svc_module, 'g') as mock_g:
            mock_g.identity = superuser_identity
            result = current_inbox_service.get_record_id_from_notification(notification)

        assert result == record["id"]

    def test_resolve_record_from_doi_url(self, running_app, search_clear, location,
                                         resource_type_v, minimal_record):
        """Full https://doi.org/ URI in context.id is also resolved correctly."""
        superuser_identity = running_app.superuser_identity
        from invenio_rdm_records.proxies import current_rdm_records
        service = current_rdm_records.records_service

        minimal_record["pids"] = {}
        draft = service.create(superuser_identity, minimal_record)
        record = service.publish(superuser_identity, draft.id)

        published_doi = record["pids"]["doi"]["identifier"]
        doi_url = f"https://doi.org/{published_doi}"

        notification = _make_notification(context_id=doi_url)

        import invenio_notify.services.service.inbox_service as svc_module
        with patch.object(svc_module, 'g') as mock_g:
            mock_g.identity = superuser_identity
            result = current_inbox_service.get_record_id_from_notification(notification)

        assert result == record["id"]

    def test_resolve_concept_doi(self, running_app, search_clear, location,
                                 resource_type_v, minimal_record):
        """Concept DOI (parent record DOI) resolves to the latest version's recid."""
        superuser_identity = running_app.superuser_identity
        from invenio_rdm_records.proxies import current_rdm_records
        service = current_rdm_records.records_service

        minimal_record["pids"] = {}
        draft = service.create(superuser_identity, minimal_record)
        record = service.publish(superuser_identity, draft.id)

        concept_doi = record["parent"]["pids"]["doi"]["identifier"]

        notification = _make_notification(context_id=concept_doi)

        import invenio_notify.services.service.inbox_service as svc_module
        with patch.object(svc_module, 'g') as mock_g:
            mock_g.identity = superuser_identity
            result = current_inbox_service.get_record_id_from_notification(notification)

        assert result == record["id"]
