from invenio_db import db
from invenio_db.uow import unit_of_work

from invenio_notify.records.models import ActorMapModel
from invenio_notify.utils import user_utils


@unit_of_work()
def add_member_to_actor(actor_id, user_id, uow=None):
    ActorMapModel.create({
        'user_id': user_id,
        'actor_id': actor_id,
    })
    user_utils.add_coarnotify_action(db, user_id)
