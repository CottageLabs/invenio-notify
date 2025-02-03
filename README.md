# How to install

Follow quick start guide in the official documentation

* https://inveniordm.docs.cern.ch/install/

```bash

# clone coarnotifypy and install it
cd coarnotifypy
pip install -e . 


cd my-site
invenio-cli packages install /your_path/invenio-notify/  


# some how my alembic upgrade not working, re-build services instead
# invenio alembic upgrade
invenio-cli services destroy
invenio-cli services setup

```

# How to send a notification to inbox

### create api access token

* go to https://127.0.0.1:5000/account/settings/applications/tokens/new/
* select scopes `notify:inbox`
* click on `Create`

### add role and create notification

```bash

# add role/action `coarnotify` to user
invenio access allow coarnotify user <user_email>

# administration-access for access admin page
invenio access allow administration-access user <user_email>

# create a notification  
# review_1.json can be found in the docs/examples/review_1.json
curl -X POST -i https://127.0.0.1:5000/api/notify-rest/inbox/somerecordid \
     -k \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ehFjcA7aOSv9YTc6rahaxGPCAETenKqt3efRVoJTVP1clBW7gUMHvB8cZ5Rs" \
     -d @$INVNOTI_NOTE/coar_examples/review_1.json
     
# check result in 
* https://127.0.0.1:5000/administration/notify-inbox?q=&l=list&p=1&s=20
```