from invenio_i18n import lazy_gettext as _

from invenio_oauth2server.models import Scope

inbox_scope = Scope(
    id_="notify:inbox",
    group="notify",
    help_text=_("Allow sending notification to the inbox."),
)
