import { withCancel } from "react-invenio-forms";
import { MEMBERS_REQUEST, MEMBERS_SUCCESS, MEMBERS_ERROR } from "../types";
import { memberApiClient } from "../../../../../api/MemberApiClient";

/**
 * Handle API errors in a consistent way
 * @param {object} error - The error object returned from the API call
 * @param {function} dispatch - Redux dispatch function
 * @param {string} defaultMessage - Default error message
 * @returns {boolean} - True if the component was unmounted, false otherwise
 */
const handleApiError = (error, dispatch, defaultMessage) => {
  if (error === "UNMOUNTED") return;

  // For debugging purposes
  if (defaultMessage) {
    console.log(`Error: ${defaultMessage}`, error);
  }

  dispatch({
    type: MEMBERS_ERROR,
    payload: error?.data || error?.errMessage || defaultMessage,
  });

  throw error;
};

/**
 * Fetch members list for a specific reviewer
 * @param {string|number} reviewerId - The ID of the reviewer
 * @returns {Promise} - Promise that resolves with the members data
 */
export const fetchMembers = (reviewerId) => {
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
      handleApiError(error, dispatch, "Failed to fetch members");
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
      dispatch(fetchMembers(reviewerId));
      
      return response.data;
    } catch (error) {
      handleApiError(error, dispatch, "Failed to add members")
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
      dispatch(fetchMembers(reviewerId));
      
      return response.data;
    } catch (error) {
      handleApiError(error, dispatch, "Failed to delete member")
    }
  };
};