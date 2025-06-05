from invenio_access import ActionUsers
from invenio_accounts.models import User

from invenio_notify.permissions import coarnotify_action


def add_coarnotify_action(db, user_id):
    action = ActionUsers.allow(coarnotify_action, user_id=user_id)
    db.session.add(action)
    db.session.commit()


def find_user_by_email(email):
    """Find user by email."""
    user = User.query.filter_by(email=email).first()
    return user