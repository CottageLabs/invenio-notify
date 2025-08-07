Overall
===================

Project Flow Description
------------------------

We have the following actors:

- **Reviewer** (e.g. PCI)
- **Repository** (e.g. Invenio notify)  
- **Record owner** - User who owns a record in repository

Flow Process
~~~~~~~~~~~~

1. Record owner sends request to Reviewer for review
2. Reviewer replies to our Repository's inbox endpoints
3. Reviewer can send multiple replies on one Record for Review status
4. After receiving notification from Reviewer, that notification will be saved in `inbox`
5. Then a background job will process those inbox notifications
6. Valid notifications like (Review, Endorsement) will be saved in database, for record landing page to display
7. If Record owner receives Reviewer's notification with endorsement status, it will show on the Record's landing page

Workflow Diagram
~~~~~~~~~~~~~~~~

.. image:: /_static/mmd/notify_workflow.png
   :alt: Invenio-Notify Workflow Sequence Diagram
   :align: center

.. note::
   For the source diagram, see ``docs/diagram/notify_workflow.mmd``
