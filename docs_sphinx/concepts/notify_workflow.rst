.. include:: ../_static/_links.rst

Notify Workflow
===================

Actors
--------------

- **Reviewer** - External peer review service that evaluates and endorses scholarly records
- **Repository** - The Invenio-based repository system that hosts and manages scholarly records  
- **Record owner** - User who owns a record in repository and requests peer review

Flow Process
------------

1. **Record owner** submits a request to **Reviewer** for peer review
2. **Reviewer** sends responses to the **Repository's** inbox endpoints
3. The **Repository** receives notifications from **Reviewer** and stores them in the inbox
4. A background job processes the inbox notifications automatically
5. Valid notifications (such as Review or Endorsement) are saved to the database and displayed on the record's landing page

.. note::
   Reviewer can send multiple notifications for one record with different statuses
   (e.g. TentativeAccept, Reject, Review, Endorsement, etc.).

.. note::
   Reviewer also can send Review or Endorsement notifications to a record without owner requesting it.

.. seealso::
   For detailed PCI (Reviewer) workflow and possible reply status, see the |pci-workflow|_.


Workflow Diagram
----------------

.. image:: /_static/mmd/notify_workflow.png
   :alt: Invenio-Notify Workflow Sequence Diagram
   :align: center
   :width: 95%

.. note::
   For the source diagram, see ``docs/diagram/notify_workflow.mmd``

