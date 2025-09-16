import axios from "axios";

const BASE_HEADERS = {
  "json": { "Content-Type": "application/json" },
  "vnd+json": {
    "Content-Type": "application/json",
    "Accept": "application/json",
  }
};

// API URL constants
const MEMBERS_API_URL = (actorId) => `/api/actor/${actorId}/members`;
const MEMBER_API_URL = (actorId) => `/api/actor/${actorId}/member`;

/**
 * API client response for member operations.
 */
export class MemberApiClientResponse {
  constructor(data, errMessage) {
    this.data = data;
    this.errMessage = errMessage;
  }
}

/**
 * API Client for actor member management.
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
   * Get members for a specific actor.
   * 
   * @param {string|number} actorId - The actor ID
   * @returns {Promise<MemberApiClientResponse>} Response with members data
   */
  async getMembers(actorId) {
    return this._createResponse(() =>
      this.axiosWithConfig.get(MEMBERS_API_URL(actorId))
    );
  }

  /**
   * Add members to a actor by email.
   * 
   * @param {string|number} actorId - The actor ID
   * @param {string[]} emails - Array of email addresses to add
   * @returns {Promise<MemberApiClientResponse>} Response with the operation result
   */
  async addMembers(actorId, emails) {
    return this._createResponse(() =>
      this.axiosWithConfig.post(MEMBERS_API_URL(actorId), { emails })
    );
  }

  /**
   * Delete a member from a actor.
   * 
   * @param {string|number} actorId - The actor ID
   * @param {string|number} userId - The user ID to remove
   * @returns {Promise<MemberApiClientResponse>} Response with the operation result
   */
  async deleteMember(actorId, userId) {
    return this._createResponse(() =>
      this.axiosWithConfig.delete(MEMBER_API_URL(actorId), {
        data: { user_id: userId },
        headers: { 'Content-Type': 'application/json' }
      })
    );
  }
}

// Export a singleton instance for direct use
export const memberApiClient = new MemberApiClient();
