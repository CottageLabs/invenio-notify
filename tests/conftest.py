from collections import namedtuple

from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import superuser_access
from invenio_access.permissions import system_identity
from invenio_administration.permissions import administration_access_action
from invenio_app.factory import create_app as _create_app
from invenio_files_rest.models import Location
from invenio_rdm_records.services.pids import providers
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from .fake_datacite_client import FakeDataCiteClient
from invenio_notify.constants import NOTIFY_PCI_ENDORSEMENT, NOTIFY_PCI_ANNOUNCEMENT_OF_ENDORSEMENT
from tests.builders.inbox_test_data_builder import *  # noqa
from tests.fixtures.endorsement_request_fixture import *  # noqa
from tests.fixtures.inbox_fixture import *  # noqa
from tests.fixtures.actor_fixture import *  # noqa
from tests.fixtures.user_fixture import *  # noqa
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.resources.serializers import DataCite43JSONSerializer

RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "superuser_identity",
        "location",
        "cache",
    ],
)


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


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photo",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photo",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "photo",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture
def location(db):
    """Create a default location for file upload."""
    loc = Location(name='local', uri='tmpxxx', default=True)
    db.session.add(loc)
    db.session.commit()
    return loc


@pytest.fixture
def rdm_record(db, superuser_identity, minimal_record, resource_type_v, location):
    """Create and publish an RDM record for testing."""
    draft = current_rdm_records.records_service.create(superuser_identity, minimal_record)
    record = current_rdm_records.records_service.publish(superuser_identity, draft.id)

    return record

def _(x):
    """Identity function for string extraction."""
    return x


@pytest.fixture(scope="module")
def mock_datacite_client():
    """Mock DataCite client."""
    return FakeDataCiteClient


@pytest.fixture(scope="module")
def app_config(app_config, mock_datacite_client):
    app_config["NOTIFY_ORIGIN_ID"] = "yoooooooooooooooooooooo"
    app_config[NOTIFY_PCI_ENDORSEMENT] = True
    app_config[NOTIFY_PCI_ANNOUNCEMENT_OF_ENDORSEMENT] = True
    
    # Enable DOI minting...
    app_config["DATACITE_ENABLED"] = True
    app_config["DATACITE_USERNAME"] = "INVALID"
    app_config["DATACITE_PASSWORD"] = "INVALID"
    app_config["DATACITE_PREFIX"] = "10.1234"
    app_config["DATACITE_DATACENTER_SYMBOL"] = "TEST"
    # ...but fake it

    app_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        # DataCite DOI provider with fake client
        providers.DataCitePIDProvider(
            "datacite",
            client=mock_datacite_client("datacite", config_prefix="DATACITE"),
            label=_("DOI"),
        ),
        # DOI provider for externally managed DOIs
        providers.ExternalPIDProvider(
            "external",
            "doi",
            validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
            label=_("DOI"),
        ),
        # OAI identifier
        providers.OAIPIDProvider(
            "oai",
            label=_("OAI ID"),
        ),
    ]
    app_config["RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        # DataCite Concept DOI provider
        providers.DataCitePIDProvider(
            "datacite",
            client=mock_datacite_client("datacite", config_prefix="DATACITE"),
            serializer=DataCite43JSONSerializer(schema_context={"is_parent": True}),
            label=_("Concept DOI"),
        ),
    ]
    
    return app_config
