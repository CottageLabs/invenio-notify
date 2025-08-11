.. include:: _static/_links.rst

Inbox API
==================================

This section documents the API endpoints provided by the Invenio-Notify module for handling 
COAR (Confederation of Open Access Repositories) notifications.

The inbox API endpoint allows external peer review services to send COAR notifications to your 
Invenio instance.

Endpoint Details
----------------

:URL: ``POST /api/notify/inbox``
:Authentication: OAuth2 with ``notify:inbox`` scope
:Content-Type: ``application/json``
:Purpose: Receives COAR notifications and performs basic payload validation. Valid 
  notifications return a 202 response, are stored in the database, and processed by 
  asynchronous background jobs

Authentication
--------------

This endpoint requires OAuth2 authentication token with the ``notify:inbox`` scope.

.. seealso::
   
   For detailed instructions on creating an access token, see :ref:`create-api-access-token` in the How-to guide.

Using the Token
^^^^^^^^^^^^^^^

Include the token in the ``Authorization`` header of your requests:

.. code-block:: http

   Authorization: Bearer YOUR_ACCESS_TOKEN

Request Format
--------------

The request body must contain a valid COAR notification in JSON-LD format.

Example Request - Endorsement Notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "@context": [
       "https://www.w3.org/ns/activitystreams",
       "https://coar-notify.net"
     ],
     "actor": {
       "id": "https://evolbiol.peercommunityin.org/coar_notify/",
       "name": "Peer Community in Evolutionary Biology",
       "type": "Service"
     },
     "context": {
       "id": "https://127.0.0.1:5000/records/drty0-qv955"
     },
     "id": "urn:uuid:94ecae36-dcfd-4182-8550-22c7164fe213",
     "object": {
       "id": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794",
       "ietf:cite-as": "https://doi.org/10.24072/pci.evolbiol.100794",
       "type": [
         "Page",
         "sorg:WebPage"
       ]
     },
     "origin": {
       "id": "https://evolbiol.peercommunityin.org/coar_notify/",
       "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
       "type": "Service"
     },
     "target": {
       "id": "https://research-organisation.org/repository",
       "inbox": "https://research-organisation.org/inbox/",
       "type": "Service"
     },
     "type": [
       "Announce",
       "coar-notify:EndorsementAction"
     ]
   }


Field Descriptions
^^^^^^^^^^^^^^^^^^

- ``id``: A unique identifier for this notification (typically a UUID). Each notification 
  must have a globally unique ID to prevent duplicate processing.

- ``type``: Notification type (see supported types below)
- ``actor.id``: **URL identifying the service or organization** sending the notification. This ID
  must be defined and configured in the Reviewer's admin page, where administrators
  manage approved reviewers and endorsers.

- ``context.id``: The complete **URL of the target record's landing page** in the repository
  (the record being reviewed or endorsed).
- ``object``: Contains details about the review or endorsement. For endorsements, the 
  ``ietf:cite-as`` field provides the **DOI that will be displayed** as a citation link on the
  record page.
- ``inReplyTo`` (optional): **Reference to an original notification ID** when this notification
  is a response or follow-up to a previous notification. For example, when a reviewer 
  replies to an endorsement request that was originally sent by a record owner through the 
  invenio-notify, this field should contain the ID of the endorsement request's notification
  to maintain proper thread continuity.

Supported Notification Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``coar-notify:ReviewAction`` - Peer review notifications
- ``coar-notify:EndorsementAction`` - Endorsement notifications
- ``TentativeAccept`` - Preliminary acceptance of review
- ``Reject`` - Rejection of review request
- ``TentativeReject`` - Preliminary rejection

.. seealso::

   |pci-workflow|_ 
   
   Complete JSON examples for all supported notification types with detailed payload structures.

Response Format
---------------

Success Response
^^^^^^^^^^^^^^^^

On successful receipt of a notification, the endpoint returns:

:Status Code: ``202 Accepted``
:Content-Type: ``application/json``

.. code-block:: json

   {
     "status": 202,
     "message": "Accepted"
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
     "message": "Missing notification ID"
   }

401 Unauthorized  
""""""""""""""""

Returned when the OAuth token is missing or invalid:

.. code-block:: json

   {
     "status": 401,
     "message": "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
   }

403 Forbidden
"""""""""""""

Returned when the actor ID doesn't match registered reviewers:

.. code-block:: json

   {
     "status": 403, 
     "message": "Actor Id mismatch"
   }

422 Unprocessable Entity
""""""""""""""""""""""""

Returned when the notification type is not supported:

.. code-block:: json

   {
     "status": 422,
     "message": "Notification type not supported"
   }

Testing
-------

To test the endpoint:

.. code-block:: bash

   curl -X POST https://your-repo.org/api/notify/inbox \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d @notification.json

Background Processing
--------------------

Notifications are processed asynchronously via Celery tasks. The system will:

- Validate the notification against COAR schemas
- Verify the target record exists and is accessible
- Check if the actor is authorized for the specific record
- Create appropriate database records (endorsements, reviews)
- Send notifications to record owners
- Update search indices

