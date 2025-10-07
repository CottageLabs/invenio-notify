"""Unit tests for the get_workflow_status function."""

import pytest
from invenio_notify import constants
from invenio_notify.tasks import get_workflow_status


class TestGetWorkflowStatus:
    """Test cases for the get_workflow_status function."""

    def test_offer_endorsement_action_returns_none(self):
        """Test Offer + coar-notify:EndorsementAction returns None (invalid for incoming replies)."""
        notification = {
            "type": ["Offer", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_ENDORSEMENT)
        assert result is None

    def test_announce_endorsement_action(self):
        """Test Announce + coar-notify:EndorsementAction returns announce_endorsement."""
        notification = {
            "type": ["Announce", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_ENDORSEMENT)
        assert result == constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT

    def test_announce_review_action(self):
        """Test Announce + coar-notify:ReviewAction returns announce_review."""
        notification = {
            "type": ["Announce", "coar-notify:ReviewAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_REVIEW)
        assert result == constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW

    def test_tentative_accept(self):
        """Test TentativeAccept returns tentative_accept."""
        notification = {
            "type": "TentativeAccept"
        }
        result = get_workflow_status(notification, constants.TYPE_TENTATIVE_ACCEPT)
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT

    def test_tentative_reject(self):
        """Test TentativeReject returns tentative_reject."""
        notification = {
            "type": "TentativeReject"
        }
        result = get_workflow_status(notification, constants.TYPE_TENTATIVE_REJECT)
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_REJECT

    def test_reject(self):
        """Test Reject returns reject."""
        notification = {
            "type": "Reject"
        }
        result = get_workflow_status(notification, constants.TYPE_REJECT)
        assert result == constants.WORKFLOW_STATUS_REJECT

    def test_tentative_accept_in_list(self):
        """Test TentativeAccept in a list returns tentative_accept."""
        notification = {
            "type": ["TentativeAccept", "SomeOtherType"]
        }
        result = get_workflow_status(notification, constants.TYPE_TENTATIVE_ACCEPT)
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT

    def test_tentative_reject_in_list(self):
        """Test TentativeReject in a list returns tentative_reject."""
        notification = {
            "type": ["SomeOtherType", "TentativeReject"]
        }
        result = get_workflow_status(notification, constants.TYPE_TENTATIVE_REJECT)
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_REJECT

    def test_reject_in_list(self):
        """Test Reject in a list returns reject."""
        notification = {
            "type": ["Reject"]
        }
        result = get_workflow_status(notification, constants.TYPE_REJECT)
        assert result == constants.WORKFLOW_STATUS_REJECT

    def test_empty_type_list(self):
        """Test empty type list returns None."""
        notification = {
            "type": []
        }
        result = get_workflow_status(notification, constants.TYPE_ENDORSEMENT)
        assert result is None

    def test_missing_type_field(self):
        """Test missing type field returns None."""
        notification = {}
        result = get_workflow_status(notification, constants.TYPE_ENDORSEMENT)
        assert result is None

    def test_none_notification_type(self):
        """Test None notification type returns None."""
        notification = {
            "type": ["Announce", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification, None)
        assert result is None

    def test_empty_notification_type(self):
        """Test empty notification type returns None."""
        notification = {
            "type": ["Announce", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification, "")
        assert result is None

    def test_unknown_activity_returns_none(self):
        """Test unknown activity with endorsement type returns None (no fallback for unsolicited)."""
        notification = {
            "type": ["SomeUnknownActivity", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_ENDORSEMENT)
        assert result is None

    def test_unknown_activity_review_returns_none(self):
        """Test unknown activity with review type returns None (no fallback for unsolicited)."""
        notification = {
            "type": ["SomeUnknownActivity", "coar-notify:ReviewAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_REVIEW)
        assert result is None

    def test_unknown_notification_type(self):
        """Test unknown notification type returns None."""
        notification = {
            "type": ["Announce", "coar-notify:UnknownAction"]
        }
        result = get_workflow_status(notification, "coar-notify:UnknownAction")
        assert result is None

    def test_offer_with_review_type_returns_none(self):
        """Test Offer activity with review type returns None (no defined combination)."""
        notification = {
            "type": ["Offer", "coar-notify:ReviewAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_REVIEW)
        # Should return None since Offer + Review is not a defined combination and no fallback
        assert result is None

    def test_announce_with_no_matching_notification_type_returns_none(self):
        """Test Announce activity with non-matching notification type returns None."""
        notification = {
            "type": ["Announce", "SomeOtherAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_ENDORSEMENT)
        # Should return None since notification type doesn't match and no fallback
        assert result is None

    def test_complex_type_with_simple_takes_precedence(self):
        """Test that simple types (like Reject) take precedence over compound types."""
        notification = {
            "type": ["Reject", "Announce", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification, constants.TYPE_ENDORSEMENT)
        # Should return reject (simple type takes precedence)
        assert result == constants.WORKFLOW_STATUS_REJECT

    def test_multiple_simple_types_first_match_wins(self):
        """Test that when multiple simple types exist, the first matching one wins."""
        notification = {
            "type": ["TentativeAccept", "Reject", "TentativeReject"]
        }
        result = get_workflow_status(notification, constants.TYPE_TENTATIVE_ACCEPT)
        # Should return tentative_accept (first match in the function's check order)
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT

    def test_real_world_examples(self):
        """Test with real-world notification examples from COAR specifications."""
        
        # Example from step 2: Request Endorsement
        notification_step2 = {
            "type": ["Offer", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification_step2, constants.TYPE_ENDORSEMENT)
        assert result is None  # Offer is outgoing, not valid for incoming replies
        
        # Example from step 5.1: Tentative Accept
        notification_step5_1 = {
            "type": "TentativeAccept"
        }
        result = get_workflow_status(notification_step5_1, constants.TYPE_TENTATIVE_ACCEPT)
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_ACCEPT
        
        # Example from step 6: Reject
        notification_step6 = {
            "type": "Reject"
        }
        result = get_workflow_status(notification_step6, constants.TYPE_REJECT)
        assert result == constants.WORKFLOW_STATUS_REJECT
        
        # Example from step 10.1: Announce Review
        notification_step10_1 = {
            "type": ["Announce", "coar-notify:ReviewAction"]
        }
        result = get_workflow_status(notification_step10_1, constants.TYPE_REVIEW)
        assert result == constants.WORKFLOW_STATUS_ANNOUNCE_REVIEW
        
        # Example from step 10.2: Announce Endorsement
        notification_step10_2 = {
            "type": ["Announce", "coar-notify:EndorsementAction"]
        }
        result = get_workflow_status(notification_step10_2, constants.TYPE_ENDORSEMENT)
        assert result == constants.WORKFLOW_STATUS_ANNOUNCE_ENDORSEMENT
        
        # Example from step 13: Tentative Reject
        notification_step13 = {
            "type": "TentativeReject"
        }
        result = get_workflow_status(notification_step13, constants.TYPE_TENTATIVE_REJECT)
        assert result == constants.WORKFLOW_STATUS_TENTATIVE_REJECT
        
        # Example from step 15: Reject (another example)
        notification_step15 = {
            "type": "Reject"
        }
        result = get_workflow_status(notification_step15, constants.TYPE_REJECT)
        assert result == constants.WORKFLOW_STATUS_REJECT