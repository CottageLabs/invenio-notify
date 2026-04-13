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

