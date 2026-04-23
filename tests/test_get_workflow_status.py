"""Unit tests for the get_workflow_status function."""

#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from unittest.mock import MagicMock

from invenio_notify import constants
from invenio_notify.workflows.endorsement import get_workflow_status


def _make_notification(type_field):
    """Build a minimal NotifyPattern stub with the given .type value."""
    n = MagicMock()
    n.type = type_field
    return n


class TestGetWorkflowStatus:
    """Test cases for the get_workflow_status function."""

    def test_offer_endorsement_action_returns_none(self):
        """Offer + coar-notify:EndorsementAction returns None (invalid for incoming replies)."""
        result = get_workflow_status(_make_notification(["Offer", "coar-notify:EndorsementAction"]))
        assert result is None

    def test_announce_endorsement_action(self):
        """Announce + coar-notify:EndorsementAction returns announce_endorsement."""
        result = get_workflow_status(_make_notification(["Announce", "coar-notify:EndorsementAction"]))
        assert result == constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT

    def test_announce_review_action(self):
        """Announce + coar-notify:ReviewAction returns announce_review."""
        result = get_workflow_status(_make_notification(["Announce", "coar-notify:ReviewAction"]))
        assert result == constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW

    def test_tentative_accept(self):
        """TentativeAccept as a string returns tentative_accept."""
        result = get_workflow_status(_make_notification("TentativeAccept"))
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT

    def test_tentative_reject(self):
        """TentativeReject as a string returns tentative_reject."""
        result = get_workflow_status(_make_notification("TentativeReject"))
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_REJECT

    def test_reject(self):
        """Reject as a string returns reject."""
        result = get_workflow_status(_make_notification("Reject"))
        assert result == constants.WORKFLOW_STATUS_REJECT

    def test_tentative_accept_in_list(self):
        """TentativeAccept in a list returns tentative_accept."""
        result = get_workflow_status(_make_notification(["TentativeAccept", "SomeOtherType"]))
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT

    def test_tentative_reject_in_list(self):
        """TentativeReject in a list returns tentative_reject."""
        result = get_workflow_status(_make_notification(["SomeOtherType", "TentativeReject"]))
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_REJECT

    def test_reject_in_list(self):
        """Reject in a list returns reject."""
        result = get_workflow_status(_make_notification(["Reject"]))
        assert result == constants.WORKFLOW_STATUS_REJECT

    def test_empty_type_list(self):
        """Empty type list returns None."""
        result = get_workflow_status(_make_notification([]))
        assert result is None

    def test_none_type_field(self):
        """None type field (unset .type on NotifyPattern) returns None."""
        result = get_workflow_status(_make_notification(None))
        assert result is None

    def test_unknown_activity_returns_none(self):
        """Unknown activity with endorsement type returns None."""
        result = get_workflow_status(_make_notification(["SomeUnknownActivity", "coar-notify:EndorsementAction"]))
        assert result is None

    def test_unknown_activity_review_returns_none(self):
        """Unknown activity with review type returns None."""
        result = get_workflow_status(_make_notification(["SomeUnknownActivity", "coar-notify:ReviewAction"]))
        assert result is None

    def test_unknown_notification_type(self):
        """Announce with unknown action type returns None."""
        result = get_workflow_status(_make_notification(["Announce", "coar-notify:UnknownAction"]))
        assert result is None

    def test_offer_with_review_type_returns_none(self):
        """Offer + ReviewAction returns None (not a defined combination)."""
        result = get_workflow_status(_make_notification(["Offer", "coar-notify:ReviewAction"]))
        assert result is None

    def test_announce_with_no_matching_notification_type_returns_none(self):
        """Announce with a non-matching action type returns None."""
        result = get_workflow_status(_make_notification(["Announce", "SomeOtherAction"]))
        assert result is None

    def test_complex_type_with_simple_takes_precedence(self):
        """Simple types like Reject take precedence over compound Announce combinations."""
        result = get_workflow_status(_make_notification(["Reject", "Announce", "coar-notify:EndorsementAction"]))
        assert result == constants.WORKFLOW_STATUS_REJECT

    def test_multiple_simple_types_first_match_wins(self):
        """When multiple simple types are present, the first match in check order wins."""
        result = get_workflow_status(_make_notification(["TentativeAccept", "Reject", "TentativeReject"]))
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT

    def test_real_world_examples(self):
        """Real-world notification examples from COAR workflow specification."""
        # Step 2: Request Endorsement (Offer — outgoing, not valid for incoming)
        assert get_workflow_status(_make_notification(["Offer", "coar-notify:EndorsementAction"])) is None

        # Step 5.1: Tentative Accept
        assert get_workflow_status(_make_notification("TentativeAccept")) == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT

        # Step 6: Reject
        assert get_workflow_status(_make_notification("Reject")) == constants.WORKFLOW_STATUS_REJECT

        # Step 10.1: Announce Review
        assert get_workflow_status(_make_notification(["Announce", "coar-notify:ReviewAction"])) == constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW

        # Step 10.2: Announce Endorsement
        assert get_workflow_status(_make_notification(["Announce", "coar-notify:EndorsementAction"])) == constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT

        # Step 13: Tentative Reject
        assert get_workflow_status(_make_notification("TentativeReject")) == constants.WORKFLOW_STATUS_TENTATIVE_REJECT

        # Step 15: Reject (second example)
        assert get_workflow_status(_make_notification("Reject")) == constants.WORKFLOW_STATUS_REJECT
