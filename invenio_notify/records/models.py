from invenio_db import db
from sqlalchemy import or_
from sqlalchemy_utils.models import Timestamp

from invenio_notify.errors import NotExistsError


class NotifyInboxModel(db.Model, Timestamp):
    __tablename__ = "notify_inbox"

    id = db.Column(db.Integer, primary_key=True)

    raw = db.Column(db.Text, nullable=False)

    @classmethod
    def create(cls, data):
        with db.session.begin_nested():
            obj = cls(
                raw=data.get("raw"),
            )
            db.session.add(obj)

        return obj

    @classmethod
    def commit(cls):
        db.session.commit()

    @classmethod
    def search(cls, search_params, filters):
        if filters == []:
            results = db.session.query(NotifyInboxModel).filter()
        else:
            results = db.session.query(NotifyInboxModel).filter(or_(*filters))

        return results

    @classmethod
    def get(cls, id):
        if obj := db.session.get(cls, id):
            return obj

        raise NotExistsError(id)

    @classmethod
    def delete(cls, obj):
        with db.session.begin_nested():
            db.session.delete(obj)
