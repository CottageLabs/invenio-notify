# How to install

Follow quick start guide in the official documentation

* https://inveniordm.docs.cern.ch/install/

```bash

# clone coarnotifypy and install it
cd coarnotifypy
pip install -e . 


cd my-site
invenio-cli packages install /your_path/invenio-notify/  
invenio-cli packages install /your_path/invenio-rdm-records/
invenio-cli packages install /your_path/invenio-app-rdm/

# some how my alembic upgrade not working, re-build services instead
# invenio alembic upgrade
invenio-cli services destroy
invenio-cli services setup

```

Features
------------------------------------
See `docs_sphinx/how_to.rst <docs_sphinx/how_to.rst>`_ for detailed instructions on how to use and test features.

## Workflow Diagram
See the [notify workflow diagram](docs/diagram/notify_workflow.mmd) to understand the complete notification process flow.


