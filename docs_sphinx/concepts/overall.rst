Notify Workflow
===================

Actors
~~~~~~~~~~~~~~

- **Reviewer** - External peer review service that evaluates and endorses scholarly records
- **Repository** - The Invenio-based repository system that hosts and manages scholarly records  
- **Record owner** - User who owns a record in repository and requests peer review

Flow Process
~~~~~~~~~~~~

1. **Record owner** sends request to **Reviewer** for review
2. **Reviewer** replies to our **Repository's** inbox endpoints
3. After receiving notification from **Reviewer**, that notification will be saved in `inbox`
4. Background job will process those inbox notifications
5. Valid notifications like (Review, Endorsement) will be saved in database, for record landing page to display
6. If **Record owner** receives a endorsement from **Reviewer**, it will show on the Record's landing page


.. note::
   Reviewer can send multiple notifications for one record with different statuses
   (e.g. TentativeAccept, Reject, Review, Endorsement, etc.).

.. note::
   Reviewer also can send Review or Endorsement notifications to a record without owner requesting it.

Workflow Diagram
~~~~~~~~~~~~~~~~

.. image:: /_static/mmd/notify_workflow.png
   :alt: Invenio-Notify Workflow Sequence Diagram
   :align: center
   :width: 95%

.. note::
   For the source diagram, see ``docs/diagram/notify_workflow.mmd``
