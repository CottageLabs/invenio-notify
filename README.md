# How to install

Follow quick start guide in the official documentation

* https://inveniordm.docs.cern.ch/install/

```bash

# clone coarnotifypy and install it
cd coarnotifypy
pip install -e . 


cd my-site
invenio-cli packages install /your_path/invenio-notify/  

# clone invenio-rdm-records that support endorsements field
invenio-cli packages install /your_path/invenio-rdm-records/

# some how my alembic upgrade not working, re-build services instead
# invenio alembic upgrade
invenio-cli services destroy
invenio-cli services setup

```

Features
------------------------------------
read docs/features.md to understand how to run or test those features


