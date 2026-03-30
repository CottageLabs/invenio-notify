
How to
=================

This guide provides step-by-step instructions for working with Invenio-Notify.


.. _create-api-access-token:

Create API access token
------------------------

Create a user who will be able to send notifications.

You will need to create an access token for the user who will send notifications.  This can only be done via the command line:

    invenio tokens create --scope=notify:inbox -n "Notify Inbox" -u <email address of user>

.. tip::
   Copy the token immediately - it is displayed only once and cannot be retrieved later from
   the website.


To create an access token via the UI (not possible unless scope is set to public, which it isn't):

1. Navigate to **Security → Applications** page in your Invenio instance
2. Click the **"New token"** button
3. User will go to create token page (https://127.0.0.1:5000/account/settings/applications/tokens/new/)
4. In the scopes selection, select **notify:inbox**
5. Click **"Create"** button



Add role and create notification
--------------------------------

1. add role/action `coarnotify` to user

   invenio access allow coarnotify user <user_email>

2. At this point you need to make a new actor record via the UI, as a general Invenio adminstrator

To create an invenio admin, make an account and give it the admin access role

    invenio users create <admin user> --password testing --active --confirm
    invenio access allow administration-access user <admin user>

3. administration-access for access admin page

    invenio notify user add <user_email> <actor_id>

for example

   invenio notify user add admina@dev.dev evolbiol.peercommunityin.org

4. create a demo notification

review_1.json can be found in the docs/examples/review_1.json, you should modify this to include your Actor ID created above

   curl -X POST -i https://127.0.0.1:5000/api/notify/inbox/somerecordid \
        -k \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <YOUR ACCESS TOKEN>" \
        -d @review_1.json

* Check the result, go to https://127.0.0.1:5000/administration/notify-inbox?q=&l=list&p=1&s=20

Add user to Actor's membership (UI)
---------------------------------------

* Go to https://127.0.0.1:5000/administration/actor
* Click ``Actions`` in the first record
* Click ``Members``
* Type ``admina@dev.dev`` in input box
* Click ``Add member``

Add user to Actor's membership (command line)
-------------------------------------------------

* Run command ``invenio notify user add admina@dev.dev "https://evolbiol.peercommunityin.org/coar_notify/"``

List Endorsements and Inbox message
------------------------------------

* Run command ``invenio notify list-notify --size 10``

Run notify background job manually (command line)
--------------------------------------------------

* Run command ``invenio notify run``