Create and manage Actors
========================

UI
--

* Go to https://127.0.0.1:5000/administration/actor
* Click ``Create`` on the top left
* Fill in the details of the Actor record as described in `docs/getting_started.rst`
* Click ``Save``

You can now:
* Edit an actor using the ``Edit`` button on the Actor row
* Delete an actor using the ``Delete`` button on the Actor row
* Modify the members of an actor using the ``Members`` button on the Actor row (see below)

Manage an Actor's membership
============================

UI
--

* Go to https://127.0.0.1:5000/administration/actor
* Click ``Actions`` on the Actor you wish to modify
* Click ``Members``

To add a user:
* Enter the user's email in input box
* Click ``Add member``

To remove a user:
* Click the ``Remove`` button on the user row

Command Line
------------

Add a user:

``invenio notify user add user@email.com <Actor ID>``

List users:

``invenio notify user list -u user@email.com``

``invenio notify user list -r <Id of actor record>``

(Note that the above command takes the integer id of the actor record NOT the COAR Actor ID)

You cannot currently remove users from an Actor via the command line, this must be done via the UI.


List Endorsements and Inbox message
===================================

UI
--

Go to https://127.0.0.1:5000/administration/notify-inbox


Command Line
------------

``invenio notify list-notify --size 10``

Run notify background job manually (command line)
=================================================

Command Line
------------

``invenio notify run``