from invenio_access import ActionUsers

from invenio_notify.permissions import coarnotify_action


def add_user_action(db, user_id):
    action = ActionUsers.allow(coarnotify_action, user_id=user_id)
    db.session.add(action)
    db.session.commit()
