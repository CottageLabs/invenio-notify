Inbox API
==================================

This section documents the API endpoints provided by the Invenio-Notify module for handling COAR (Confederation
of Open Access Repositories) notifications.

The inbox API endpoint allows external peer review services to send COAR notifications to your Invenio instance.

Endpoint Details
----------------

:URL: ``POST /api/notify/inbox``
:Authentication: OAuth2 with ``notify:inbox`` scope
:Content-Type: ``application/json``
:Purpose: Receives COAR notifications and performs basic payload validation. Valid notifications return a 202 response, are stored in the database, and processed by asynchronous background jobs

Authentication
--------------

This endpoint requires OAuth2 authentication with the ``notify:inbox`` scope. 

Creating an Access Token
^^^^^^^^^^^^^^^^^^^^^^^^^

To create an access token:

1. Navigate to **Security → Applications** page in your Invenio instance
2. Click the **"New token"** button
3. In the scopes selection, select **notify:inbox**
4. Click **"Create"** button

.. tip::
   Copy the token immediately - it is displayed only once and cannot be retrieved later from the website.

Using the Token
^^^^^^^^^^^^^^^

Include the token in the ``Authorization`` header of your requests:

.. code-block:: http

   Authorization: Bearer YOUR_ACCESS_TOKEN

Request Format
--------------

The request body must contain a valid COAR notification in JSON-LD format. The notification must include:

- ``@context``: COAR notification context URLs
- ``type``: Notification type (see supported types below)
- ``actor``: Information about the sender
- ``object``: The resource being reviewed/endorsed
- ``inReplyTo`` (optional): Reference to original notification for replies

Supported Notification Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``coar-notify:ReviewAction`` - Peer review notifications
- ``coar-notify:EndorsementAction`` - Endorsement notifications
- ``TentativeAccept`` - Preliminary acceptance of review
- ``Reject`` - Rejection of review request
- ``TentativeReject`` - Preliminary rejection

Example Request - Review Notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "@context": [
       "https://www.w3.org/ns/activitystreams",
       "https://purl.org/coar/notify"
     ],
     "type": "coar-notify:ReviewAction",
     "actor": {
       "type": "Service",
       "id": "https://review-service.example.org/",
       "name": "Peer Review Service"
     },
     "object": {
       "type": "sorg:ScholarlyArticle",
       "id": "https://your-repo.org/records/12345",
       "ietf:cite-as": "https://doi.org/10.5555/12345"
     },
     "context": {
       "type": "sorg:Review",
       "id": "https://review-service.example.org/reviews/67890",
       "url": [
         {
           "id": "https://review-service.example.org/reviews/67890/content",
           "mediaType": "text/html"
         }
       ]
     }
   }

Example Request - Endorsement Notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "@context": [
       "https://www.w3.org/ns/activitystreams",
       "https://purl.org/coar/notify"
     ],
     "type": "coar-notify:EndorsementAction",
     "actor": {
       "type": "Service",
       "id": "https://endorsement-service.example.org/",
       "name": "Research Endorsement Platform"
     },
     "object": {
       "type": "sorg:ScholarlyArticle",
       "id": "https://your-repo.org/records/12345",
       "ietf:cite-as": "https://doi.org/10.5555/12345"
     },
     "context": {
       "type": "sorg:Endorsement",
       "id": "https://endorsement-service.example.org/endorsements/98765"
     }
   }

Example Request - Reply Notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "@context": [
       "https://www.w3.org/ns/activitystreams",
       "https://purl.org/coar/notify"
     ],
     "type": "TentativeAccept",
     "actor": {
       "type": "Person",
       "id": "https://orcid.org/0000-0000-0000-0000",
       "name": "Jane Reviewer"
     },
     "object": {
       "type": "sorg:ScholarlyArticle",
       "id": "https://your-repo.org/records/12345",
       "ietf:cite-as": "https://doi.org/10.5555/12345"
     },
     "inReplyTo": {
       "type": "coar-notify:ReviewAction",
       "id": "https://your-repo.org/notifications/original-123"
     }
   }

Response Format
---------------

Success Response
^^^^^^^^^^^^^^^^

On successful receipt of a notification, the endpoint returns:

:Status Code: ``202 Accepted``
:Content-Type: ``application/json``

.. code-block:: json

   {
     "status": "received",
     "message": "Notification received and queued for processing"
   }

The notification is queued for asynchronous background processing, which includes:

- Creating endorsement records
- Sending notifications to record owners  
- Updating search indices
- Processing any reply notifications

Error Responses
^^^^^^^^^^^^^^^

The endpoint may return the following error responses:

400 Bad Request
"""""""""""""""

Returned when the request data is missing or invalid:

.. code-block:: json

   {
     "status": 400,
     "message": "Invalid notification format",
     "errors": ["Missing required field: actor"]
   }

401 Unauthorized  
""""""""""""""""

Returned when the OAuth token is missing or invalid:

.. code-block:: json

   {
     "status": 401,
     "message": "Valid authentication required"
   }

403 Forbidden
"""""""""""""

Returned when the actor ID doesn't match registered reviewers:

.. code-block:: json

   {
     "status": 403, 
     "message": "Actor not authorized for this record"
   }

422 Unprocessable Entity
""""""""""""""""""""""""

Returned when the notification type is not supported:

.. code-block:: json

   {
     "status": 422,
     "message": "Unsupported notification type"
   }

Integration Guide
-----------------

Setup for External Services
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To integrate with this endpoint, external services should:

1. **Register as OAuth Client**: Contact the repository administrator to register as an OAuth2 client application.

2. **Obtain Access Token**: Use the OAuth2 client credentials flow to obtain an access token with ``notify:inbox`` scope.

3. **Validate Notification Format**: Ensure notifications follow the COAR notification specification with proper JSON-LD structure.

4. **Handle Responses**: Implement proper error handling for all possible response codes.

5. **Register Reviewers**: Ensure reviewer/endorser IDs are properly registered with the target repository.

Testing
^^^^^^^

To test the endpoint:

.. code-block:: bash

   curl -X POST https://your-repo.org/api/notify/inbox \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d @notification.json

Background Processing
^^^^^^^^^^^^^^^^^^^^

Notifications are processed asynchronously via Celery tasks. The system will:

- Validate the notification against COAR schemas
- Verify the target record exists and is accessible  
- Check if the actor is authorized for the specific record
- Create appropriate database records (endorsements, reviews)
- Send notifications to record owners
- Update search indices

Monitor the Celery worker logs for processing status and any errors that occur during background processing.

Related Documentation
--------------------

- :doc:`workflow` - Overview of the complete notification workflow
- :doc:`database_schema` - Database models and relationships
- :doc:`configuration` - Configuration options for notification processing