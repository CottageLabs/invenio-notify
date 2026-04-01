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

(Note that ``setuptools`` may not be necessary here, but is include to avoid a potential issue with the latest version of setuptools and ``pkg_resources`` deprecation/removal)

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


Configuration
=============

TODO
