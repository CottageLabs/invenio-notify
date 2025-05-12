import { http, withCancel } from "react-invenio-forms";
import { MEMBERS_REQUEST, MEMBERS_SUCCESS, MEMBERS_ERROR } from "../types";

// API URL constants
const MEMBERS_API_URL = (reviewerId) => `/api/reviewer/${reviewerId}/members`;
const MEMBER_API_URL = (reviewerId) => `/api/reviewer/${reviewerId}/member`;

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

    const apiUrl = MEMBERS_API_URL(reviewerId);
    
    try {
      const cancellableRequest = withCancel(http.get(apiUrl));
      const response = await cancellableRequest.promise;
      
      const members = response.data.hits || [];
      
      dispatch({
        type: MEMBERS_SUCCESS,
        payload: members,
      });

      return members;
    } catch (error) {
      if (error === "UNMOUNTED") return;
      
      dispatch({
        type: MEMBERS_ERROR,
        payload: error?.response?.data?.message || error?.message,
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

    const apiUrl = MEMBERS_API_URL(reviewerId);
    
    try {
      const cancellableRequest = withCancel(
        http.post(apiUrl, { emails })
      );
      const response = await cancellableRequest.promise;
      
      // Refresh members list after adding
      dispatch(getMembers(reviewerId));
      
      return response.data;
    } catch (error) {
      if (error === "UNMOUNTED") return;
      
      dispatch({
        type: MEMBERS_ERROR,
        payload: error?.response?.data?.message || error?.message,
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

    const apiUrl = MEMBER_API_URL(reviewerId);
    
    try {
      const cancellableRequest = withCancel(
        http.delete(apiUrl, {
          data: { user_id: memberId },
          headers: { 'Content-Type': 'application/json' }
        })
      );
      const response = await cancellableRequest.promise;
      
      // Refresh members list after deletion
      dispatch(getMembers(reviewerId));
      
      return response.data;
    } catch (error) {
      if (error === "UNMOUNTED") return;
      
      dispatch({
        type: MEMBERS_ERROR,
        payload: error?.response?.data?.message || error?.message,
      });

      throw error;
    }
  };
};