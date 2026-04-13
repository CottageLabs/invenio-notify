Installation
============

(To install for development, see `docs/development.rst`)

1. You will need an InvenioRDM instance into which to install this module.

Acquire a suitable InvenioRDM instance, and configure it as follows:

In your ``site/pyproject.toml`` (create this if it does not exist)

.. code-block:: toml

    [project]
    name = "<your site name>"
    version = "<your version>"
    dependencies = [
        "invenio-notify @ git+https://github.com/CottageLabs/invenio-notify.git",
        "setuptools<81.0.0"
    ]

(Note that ``setuptools`` may not be necessary here, but is included to avoid a potential issue with the latest version of setuptools and ``pkg_resources`` deprecation/removal)

2. Configure your InvenioRDM instance to override any of the module's configuration values for your local requirements.  See the section below on Configuration options.

3. Follow a regular installation process for your InvenioRDM instance, which will install the module as a dependency.

Once this is done, you can log into the system as an administrator and see the Notify capabilities.

Creating an admin user with the appropriate permissions:

.. code-block:: bash

    invenio users create admin@email.com --password <password> --active --confirm
    invenio access allow administration-access user admin@email.com

To add users with notify capabilities, go to the `docs/getting_started.rst` file and follow the instructions there.

4. In order to be able to display endorsements and reviews, you need to update your index mappings, which you can do with this command:

.. code-block:: bash

    curl -XPUT -H "Content-Type: application/json" -d @invenio-notify/invenio_notify/records/mappings/notify-record-v8.0.0.json http://localhost:9200/<record-index-name>/_mapping

5. To be able to process incoming notifications you will need to set up the regular processing job.  You can do this as a superuser in the admin area as follows:

* Go to https://127.0.0.1:5000/administration/jobs
* Click "Create" on the top left
* Fill in the details as follows (free-text fields can be amended as desired):
 * Name: "Process notify inbox"
 * Description: "Process incoming notifications using the configured workflows"
 * Queue: Low (or whatever queue you want to use for this job)
 * Task: "Process notify inbox" (this is the name of the task registered by the module, and will be available in the dropdown list)
 * Active: checked

You can also run this job manually from the command line with:

.. code-block:: bash

    invenio notify run

This will run the job one-time, so you would need to set this up with a cron job or other scheduler to run it on a regular basis.


Configuration
=============

Basic configuration
-------------------

The primary configuration you may want to set are as follows:

* ``NOTIFY_ORIGIN_ID`` - this specifies the URL which will be used in the `origin.id` field of all outgoing notifications.  See https://coar-notify.net/specification/1.0.1/ for more details on this field and its purpose.

* ``NOTIFY_ENDORSEMENT_RECEIVE`` - defaults to `True` and enables the ability to receive endorsement and review notifications for actors using the Endorsement workflow.  If set to true, while NOTIFY_ENDORSEMENT_REQUEST is set to False your repository will support only this workflow: https://coar-notify.net/catalogue/workflows/pci-sciety/

* ``NOTIFY_ENDORSEMENT_REQUEST`` - defaults to `True` and enables the ability to send endorsement requests, and thus enables the full Endorsement workflow as documented here https://coar-notify.net/catalogue/workflows/repository-pci/.  For this to work ``NOTIFY_ENDORSEMENT_RECEIVE`` MUST be set to True.


Webpack Setup
-------------

In order to load the notify javascript widgets on the details pages, you will need to add the notify webpack settings.  In your ``site/<instance_name>/webpack.py` file, add/merge the following:

.. code-block:: python

    theme = WebpackThemeBundle(
        __name__,
        "assets",
        default="semantic-ui",
        themes={
            "semantic-ui": dict(
                entry={
                    "notify": "./js/invenio_notify/src/landing_page/notify.js"
                },
            ),
        },
    )



Search configuration
--------------------

If you want to add facets to the search results to enable filtering by reviews, you can add the following facet to your configuration:

.. code-block:: python

    from invenio_i18n import lazy_gettext as _

    has_reviews = TermsFacet(
        field="notify.has_reviews",
        label=_("Has reviews"),
        value_labels={"true": _("Yes"), "false": _("No")},
    )

    RDM_FACETS["has_reviews"] = {
        "facet": has_reviews,
        "ui": {
            "field": "notify.has_reviews",
        },
    }

    RDM_SEARCH["facets"].append("has_reviews")