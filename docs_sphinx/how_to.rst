
How to
=================

This guide provides step-by-step instructions for working with Invenio-Notify.


.. _create-api-access-token:

Create API access token
------------------------

To create an access token:

1. Navigate to **Security → Applications** page in your Invenio instance
2. Click the **"New token"** button
3. User will go to create token page (https://127.0.0.1:5000/account/settings/applications/tokens/new/)
4. In the scopes selection, select **notify:inbox**
5. Click **"Create"** button

.. tip::
   Copy the token immediately - it is displayed only once and cannot be retrieved later from 
   the website.

Add role and create notification
--------------------------------

.. code-block:: bash

   # add role/action `coarnotify` to user
   invenio access allow coarnotify user <user_email>

   # administration-access for access admin page
   invenio notify user add <user_email> <reviewer_id>
   # example
   invenio notify user add admina@dev.dev evolbiol.peercommunityin.org

   # create a notification  
   # review_1.json can be found in the docs/examples/review_1.json
   curl -X POST -i https://127.0.0.1:5000/api/notify/inbox/somerecordid \
        -k \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ehFjcA7aOSv9YTc6rahaxGPCAETenKqt3efRVoJTVP1clBW7gUMHvB8cZ5Rs" \
        -d @$INVNOTI_NOTE/coar_examples/review_1.json

* Check the result, go to https://127.0.0.1:5000/administration/notify-inbox?q=&l=list&p=1&s=20

Add user to Reviewer's membership (UI)
---------------------------------------

* Go to https://127.0.0.1:5000/administration/reviewer
* Click ``Actions`` in the first record
* Click ``Members``
* Type ``admina@dev.dev`` in input box
* Click ``Add member``

Add user to Reviewer's membership (command line)
-------------------------------------------------

* Run command ``invenio notify user add admina@dev.dev "https://evolbiol.peercommunityin.org/coar_notify/"``

List Endorsements and Inbox message
------------------------------------

* Run command ``invenio notify list-notify --size 10``

Run notify background job manually (command line)
--------------------------------------------------

* Run command ``invenio notify run``