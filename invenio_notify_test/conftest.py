from collections import namedtuple

import pytest
from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import superuser_access
from invenio_administration.permissions import administration_access_action
from invenio_app.factory import create_app as _create_app

RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "superuser_identity",
        "location",
        "cache",
    ],
)


# @pytest.fixture(scope="module")
# def extra_entry_points():
#     """Register extra entry point."""
#     return {
#         "invenio_administration.views": [
#             "mock_module = mock_module.administration.mock:MockView",
#             "mock_module = mock_module.administration.mock:MockViewAlternate",
#         ],
#         "invenio_base.apps": [
#             "test = mock_module.ext:MockExtension",
#         ],
#     }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app


@pytest.fixture
def running_app(
        app,
        superuser_identity,
        location,
        cache,
):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(
        app,
        superuser_identity,
        location,
        cache,
    )


@pytest.fixture
def test_app(running_app):
    """Get current app."""
    return running_app.app


@pytest.fixture
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(u.user, "admin-access")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    return u


@pytest.fixture
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="admin-access", id="admin-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=administration_access_action, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


import pytest
from invenio_rdm_records.records import RDMParent, RDMRecord


@pytest.fixture
def minimal_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "publication_date": "2020-06-01",
            # because DATACITE_ENABLED is True, this field is required
            "publisher": "Acme Inc",
            "resource_type": {"id": "image-photo"},
            "title": "A Romans story",
        },
    }


def prepare_test_rdm_record(db, record_data):
    parent = RDMParent.create({})
    record = RDMRecord.create(record_data, parent=parent)
    db.session.commit()
    return record


@pytest.fixture
def create_rdm_record(db, minimal_record):
    """Create an RDM record and return its ID."""
    parent = RDMParent.create({})
    record = RDMRecord.create(minimal_record, parent=parent)
    db.session.commit()
    return record


def create_endorsement_service_data(record_id, inbox_id, user_id):
    return {
        'metadata': {
            'record_id': record_id
        },
        'record_id': record_id,
        'reviewer_id': 'reviewer-123',
        'review_type': 'endorsement',
        'user_id': user_id,
        'inbox_id': inbox_id,
    }


def create_notification_data(record_id):
    """Create notification data with a real record ID."""

    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "name": "Peer Community in Evolutionary Biology",
            "type": "Service"
        },
        "context": {
            "id": f"https://127.0.0.1:5000/records/{record_id}"
        },
        "id": "urn:uuid:94ecae35-dcfd-4182-8550-22c7164fe23f",
        "inReplyTo": "urn:uuid:0370c0fb-bb78-4a9b-87f5-bed307a509dd",
        "object": {
            "id": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794#review-3136",
            "ietf:cite-as": "",
            "type": [
                "Page",
                "sorg:WebPage"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": [
            "Announce",
            "coar-notify:ReviewAction"
        ]
    }
