Getting Started
===============

This guide provides step-by-step instructions for working with Invenio-Notify.

.. _create-api-access-token:

Create User and API access token
--------------------------------

1. Create a user who will be able to send notifications.

.. code-block::

    invenio users create user@email.com --password <password> --active --confirm

2. Give create an access token with the ``notify:inbox`` scope.  Note that this is an internal scope, you cannot give this scope to users via the User Interface.

.. code-block::

    invenio tokens create --scope=notify:inbox -n "Notify Inbox" -u user@email.com

The token will be output on the command line, you should copy it and keep it safe immediately, it cannot be recovered at a later time.

3. Confirming the access token

Go to the Application section of your user settings https://127.0.0.1:5000/account/settings/applications/

You should see your new Personal access token listed there.  As the nature of the ``notify:inbox`` scope is internal, you will not be able to see the scope of the token here, but you can confirm that it is working by using it to send a notification as described below.


Add the notify role to the user
-------------------------------

1. add role/action `coarnotify` to user

.. code-block::

   invenio access allow coarnotify user user@email.com

2. Create a COAR Notify Actor record in the system.

This must be done via the User Interface, go to ``Administration -> Notify -> Actors``: https://127.0.0.1:5000/administration/actor

Click "Create" on the top left, and enter the details:

* Name: a full name to identify the actor, e.g. ``PCI Evolutionary Biology``
* Actor id: This is the Identifier that the actor will use to identify themselves.  This will likely be a URI such as ``https://evolbiol.peercommunityin.org/coar_notify/``
* Inbox url: if the actor ALSO provides an Inbox to which InvenioRDM may send notifications, enter it here, if not leave it blank.  For example ``https://evolbiol.peercommunityin.org/coar_notify/inbox/``
* Inbox api token: If the Inbox URL provided in the previous field must be accessed with an access/api token, to authenticate your InvenioRDM instance with the service, enter it here.  If not, leave it blank.
* Description: A description of the Actor for your convenience.

Click "Save" and you will see your new actor record.

Create as many actor records as you need at this stage.  Each unique Actor ID will require its own record.


3. Give a user rights to send notifications using the Actor ID.

Users will send notifications to the notify inbox using their access token.  Their notifications will contain an Actor ID.  The Actor ID they supply must match one that they are permitted to use.

To do this, add the Actor ID to their user account:

.. code-block::

    invenio notify user add <user_email> <actor_id>

for example

.. code-block::

   invenio notify user add user@email.com https://evolbiol.peercommunityin.org/coar_notify/

You may add as many users as you like to an Actor ID, and as many Actor IDs as you like to users.


Create a demo notification
--------------------------

1. Choose a notification to send from the ``docs/examples`` directory.  For example ``announce_review.json``

2. Make a copy of this notification into a temporary location

3. Edit the notification as follows:

 * ensure the ``actor.id`` property matches one of your actors
 * ensure the ``context.id`` matches a URL of a record in your Invenio instance

4. Post the notification to the repository inbox

.. code-block::

   curl -X POST -i https://127.0.0.1:5000/api/notify/inbox \
        -k \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <YOUR ACCESS TOKEN>" \
        -d @<your_notification.json>

Replace ``<YOUR ACCESS TOKEN>`` with the ``notify:inbox`` scoped access token created earlier.  This token must belong to a user who is associated with the Actor ID as described above.

Replace ``<your_notification.json>`` with the path to the notification you wish to send.

5. Check the results

As an administrator, go to https://127.0.0.1:5000/administration/notify-inbox

You should see your notification listed.


