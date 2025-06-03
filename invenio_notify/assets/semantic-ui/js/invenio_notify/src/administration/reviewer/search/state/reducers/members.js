import { MEMBERS_REQUEST, MEMBERS_SUCCESS, MEMBERS_ERROR } from "../types";

/**
 * Initial state for the members reducer
 */
export const initialState = {
  data: [],
  loading: false,
  error: null,
};

/**
 * Members reducer
 * 
 * Handles state changes for member-related actions:
 * - Loading state when requests are in progress
 * - Success state with data when requests complete successfully
 * - Error state when requests fail
 * 
 * @param {Object} state - Current state
 * @param {Object} action - Action being dispatched
 * @returns {Object} New state
 */
export const membersReducer = (state = initialState, action) => {
  switch (action.type) {
    case MEMBERS_REQUEST:
      return {
        ...state,
        loading: true,
        error: null,
      };

    case MEMBERS_SUCCESS:
      return {
        ...state,
        data: action.payload,
        loading: false,
        error: null,
      };

    case MEMBERS_ERROR:
      return {
        ...state,
        loading: false,
        error: action.payload,
      };

    default:
      return state;
  }
};

export default membersReducer;