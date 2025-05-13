import { withCancel } from "react-invenio-forms";
import { MEMBERS_REQUEST, MEMBERS_SUCCESS, MEMBERS_ERROR } from "../types";
import { memberApiClient } from "../../../../../api/MemberApiClient";
// KTODO refactor try and error handling

/**
 * Fetch members list for a specific reviewer
 * @param {string|number} reviewerId - The ID of the reviewer
 * @returns {Promise} - Promise that resolves with the members data
 */
export const getMembers = (reviewerId) => {
  return async (dispatch) => {
    dispatch({
      type: MEMBERS_REQUEST,
    });
    
    try {
      const cancellableRequest = withCancel(memberApiClient.getMembers(reviewerId));
      const response = await cancellableRequest.promise;
      
      const members = response.data.hits || [];
      
      dispatch({
        type: MEMBERS_SUCCESS,
        payload: members,
      });

      return members;
    } catch (error) {
      console.log("Error fetching members:", error);
      if (error === "UNMOUNTED") return;
      
      dispatch({
        type: MEMBERS_ERROR,
        payload: error?.data || "Failed to fetch members",
      });

      throw error;
    }
  };
};

/**
 * Add members to a reviewer
 * @param {string|number} reviewerId - The ID of the reviewer
 * @param {string[]} emails - Array of email addresses to add as members
 * @returns {Promise} - Promise that resolves with the response data
 */
export const addMembers = (reviewerId, emails) => {
  return async (dispatch) => {
    dispatch({
      type: MEMBERS_REQUEST,
    });
    
    try {
      const cancellableRequest = withCancel(
        memberApiClient.addMembers(reviewerId, emails)
      );
      const response = await cancellableRequest.promise;
      
      // Refresh members list after adding
      dispatch(getMembers(reviewerId));
      
      return response.data;
    } catch (error) {
      if (error === "UNMOUNTED") return;
      
      dispatch({
        type: MEMBERS_ERROR,
        payload: error?.errMessage || "Failed to add members",
      });

      throw error;
    }
  };
};

/**
 * Delete a member from a reviewer
 * @param {string|number} reviewerId - The ID of the reviewer
 * @param {string|number} memberId - The ID of the member to delete
 * @returns {Promise} - Promise that resolves with the response data
 */
export const deleteMember = (reviewerId, memberId) => {
  return async (dispatch) => {
    dispatch({
      type: MEMBERS_REQUEST,
    });
    
    try {
      const cancellableRequest = withCancel(
        memberApiClient.deleteMember(reviewerId, memberId)
      );
      const response = await cancellableRequest.promise;
      
      // Refresh members list after deletion
      dispatch(getMembers(reviewerId));
      
      return response.data;
    } catch (error) {
      if (error === "UNMOUNTED") return;
      
      dispatch({
        type: MEMBERS_ERROR,
        payload: error?.errMessage || "Failed to delete member",
      });

      throw error;
    }
  };
};