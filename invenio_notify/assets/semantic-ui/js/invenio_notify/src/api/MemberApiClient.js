import axios from "axios";

const BASE_HEADERS = {
  "json": { "Content-Type": "application/json" },
  "vnd+json": {
    "Content-Type": "application/json",
    "Accept": "application/json",
  }
};

// API URL constants
const MEMBERS_API_URL = (reviewerId) => `/api/reviewer/${reviewerId}/members`;
const MEMBER_API_URL = (reviewerId) => `/api/reviewer/${reviewerId}/member`;

/**
 * API client response for member operations.
 */
export class MemberApiClientResponse {
  constructor(data, errors) {
    this.data = data;
    this.errors = errors;
  }
}

/**
 * API Client for reviewer member management.
 */
export class MemberApiClient {
  constructor(additionalApiConfig = {}) {
    const additionalHeaders = additionalApiConfig.headers || {};
    this.apiHeaders = Object.assign({}, BASE_HEADERS, additionalHeaders);

    this.apiConfig = {
      withCredentials: true,
      xsrfCookieName: "csrftoken",
      xsrfHeaderName: "X-CSRFToken",
      headers: this.apiHeaders["vnd+json"],
    };
    this.axiosWithConfig = axios.create(this.apiConfig);
  }

  /**
   * Creates a response object from an axios request.
   * 
   * @param {Function} axiosRequest - Function that returns an axios Promise
   * @returns {Promise<MemberApiClientResponse>} Response object
   */
  async _createResponse(axiosRequest) {
    try {
      const response = await axiosRequest();
      return new MemberApiClientResponse(response.data || {}, []);
    } catch (error) {
      let errorData = error.response?.data || {};
      throw new MemberApiClientResponse({}, errorData.message || "An error occurred");
    }
  }

  /**
   * Get members for a specific reviewer.
   * 
   * @param {string|number} reviewerId - The reviewer ID
   * @returns {Promise<MemberApiClientResponse>} Response with members data
   */
  async getMembers(reviewerId) {
    return this._createResponse(() =>
      this.axiosWithConfig.get(MEMBERS_API_URL(reviewerId))
    );
  }

  /**
   * Add members to a reviewer by email.
   * 
   * @param {string|number} reviewerId - The reviewer ID
   * @param {string[]} emails - Array of email addresses to add
   * @returns {Promise<MemberApiClientResponse>} Response with the operation result
   */
  async addMembers(reviewerId, emails) {
    return this._createResponse(() =>
      this.axiosWithConfig.post(MEMBERS_API_URL(reviewerId), { emails })
    );
  }

  /**
   * Delete a member from a reviewer.
   * 
   * @param {string|number} reviewerId - The reviewer ID
   * @param {string|number} userId - The user ID to remove
   * @returns {Promise<MemberApiClientResponse>} Response with the operation result
   */
  async deleteMember(reviewerId, userId) {
    return this._createResponse(() =>
      this.axiosWithConfig.delete(MEMBER_API_URL(reviewerId), {
        data: { user_id: userId },
        headers: { 'Content-Type': 'application/json' }
      })
    );
  }
}

// Export a singleton instance for direct use
export const memberApiClient = new MemberApiClient();
