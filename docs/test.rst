Testing
=======

Unsolicited Endorsements
------------------------

1. Send an unsolicited endorsement to the system

You will need the following:

* An access token for a user with permissions to send notifications using the Actor ID you will use in the notification.  See `docs/getting_started.rst` for instructions on how to set this up.

* A copy of the ``docs/examples/unsolicited_announce_endorsement.json`` file.  You will need to edit to this to replace the placeholder values:
 * ``{actor_id}`` - An Actor ID that you have set up in Invenio for this test.
 * ``{record_url}`` - The web URL for a record in your Invenio instance
 * ``{actor_inbox}`` - The inbox URL for the Actor ID you are using.

Run the following CURL command to post the notification to the inbox.  Replace ``<YOUR ACCESS TOKEN>`` and ``<your_notification.json>`` with the appropriate values.

.. code-block::

   curl -X POST -i https://127.0.0.1:5000/api/notify/inbox \
        -k \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <YOUR ACCESS TOKEN>" \
        -d @<your_notification.json>

2. Check the endorsement has arrived

Go to https://127.0.0.1:5000/administration/notify-inbox

You should see the endorsement notification listed.


3. Send a related unsolicited review to the system

Repeat the above steps, but using the ``docs/examples/unsolicited_announce_review.json`` file instead.  Again, ensure you replace the placeholder values in the notification with appropriate values for your system.

4. Check the review has arrived

Go to https://127.0.0.1:5000/administration/notify-inbox

You should see the both the review and endorsement notifications listed.


5. Run the workflow processor

On the command line, run the following command to process the notifications:

.. code-block::

    invenio notify run

6. Check that the notifications have been processed.

Go to https://127.0.0.1:5000/administration/notify-inbox

You should see the both the review and endorsement notifications listed with a "Process Date" showing they were recently processed.


Full Endorsements Workflow
--------------------------

Setup
^^^^^

1. You will need an external COAR Notify inbox to receive notifications from your InvenioRDM instance.

The Python library used by this module can provide a local Notify inbox that you can use for such testing.  Full documentation for this is here https://coar-notify.github.io/coarnotifypy/build/html/test_server.html

Set up a local test server and start it with

.. code-block:: console

    export COARNOTIFY_SETTINGS=/path/to/local.cfg; python coarnotify/test/server/inbox.py

You will now be able to check for any notifications sent by InvenioRDM to that inbox in the directory you specified
in the ``STORE_DIR`` property of your local settings file.

2. You will need to set the Actor for your external inbox from step (1).

In your InvenioRDM instance, go to https://127.0.0.1:5000/administration/actor as an administrator and add an Actor
record which gives http://127.0.0.1:5005/inbox as the inbox URL.  (The Actor ID can be any URL, but for clarity it's best to use the inbox URL as the Actor ID in this case).

3. Add your user who will send notifications to the Actor you just created.

Go to https://127.0.0.1:5000/administration/actor and select Members from under Actions, and add the user account.


Successful Endorsement Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. See the Endorsement Request options

Go to a record details page in your InvenioRDM instance for a record that you are the owner of (you may impersonate
the owner if you are an administrator).

On the right you should find an "Endorsement Request" section, which includes the test inbox you created during setup.

2. Send an endorsement request

Select the test inbox from the sidebar widget and click "Request".  After a short pause you should see a message
saying your endorsement request has been successfully sent.

You will also see that the Test inbox is no longer available in the pull-down list, as you can only have one active endorsement request at a time for a given Actor.

In the status table below you will see the test inbox listed with a status of "Pending".

3. Check the endorsement request has arrived in the test inbox

Go to the directory you specified in the ``STORE_DIR`` property of your local settings file for the test server.  You
should see a file which starts with the timestamp of when you sent the notification.

Open the file and confirm that there is a suitable JSON endorsement request.

4. See the endorsement request in the admin area

Go to https://127.0.0.1:5000/administration/endorsement-request to see the endorsement request that was issued

5. Issue a Tentative Accept notification from the test inbox

Make a copy of the ``endorsement_tentatively_accept.json`` file from the ``docs/examples`` directory and edit it to replace the placeholder values with appropriate values for your system, ensuring that the ``inReplyTo`` field matches the id of the endorsement request you just sent.

Post this notification to the test inbox with the following command, replacing ``<your_notification.json>`` with the path to your edited notification:

Run the following CURL command to post the notification to the inbox.  Replace ``<YOUR ACCESS TOKEN>`` and ``<endorsement_tentatively_accept_local.json>`` with the appropriate values.

.. code-block::

   curl -X POST -i https://127.0.0.1:5000/api/notify/inbox \
        -k \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <YOUR ACCESS TOKEN>" \
        -d @<endorsement_tentatively_accept_local.json>

6. Check the Tentative Accept notification has been received

Go to https://127.0.0.1:5000/administration/notify-inbox and see the notification in the inbox

7. Run the workflow processor

On the command line, run the following command to process the notifications:

.. code-block::

    invenio notify run

When you reload the page at https://127.0.0.1:5000/administration/notify-inbox you should see the tentatively accepted notification
has been processed

8. Check that the status of the endorsement request has updated

Go to the record page from which you requested an endorsement, ensuring you are logged in as the record owner,
and check that the status for the test inbox has been updated to "In progress".

9. Send the endorsement and a review from the test actor

Make copies of ``endorsement_announce_endorsement.json`` and ``endorsement_announce_review.json`` from the ``docs/examples`` directory, and edit them to replace the placeholder values with appropriate values for your system, ensuring that the ``inReplyTo`` field in both notifications matches the id of the endorsement request you sent.

Run the following CURL commands to post the notifications to the inbox.  Replace ``<YOUR ACCESS TOKEN>`` and ``<endorsement_announce_endorsement_local.json>`` and ``<endorsement_announce_review_local.json>`` with the appropriate values.

.. code-block::

   curl -X POST -i https://127.0.0.1:5000/api/notify/inbox \
        -k \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <YOUR ACCESS TOKEN>" \
        -d @<endorsement_announce_endorsement_local.json>

.. code-block::

   curl -X POST -i https://127.0.0.1:5000/api/notify/inbox \
        -k \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <YOUR ACCESS TOKEN>" \
        -d @<endorsement_announce_review_local.json>

10. Run the workflow processor again

On the command line, run the following command to process the notifications:

.. code-block::

    invenio notify run

11. Check the endorsement and review have been processed

Go to the record page as the record owner.  You should find that endorsement/review appear in the Endorsements side panel.

Meanwhile, the Test Inbox is no longer listed in the Endorsement Request section of the sidebar, as the endorsement request has now been completed.