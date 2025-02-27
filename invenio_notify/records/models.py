from invenio_db import db
from invenio_records.models import RecordMetadataBase
from sqlalchemy import or_
from sqlalchemy_utils.models import Timestamp

from invenio_notify.errors import NotExistsError


class DbOperationMixin:
    @classmethod
    def commit(cls):
        db.session.commit()

    @classmethod
    def delete(cls, obj):
        with db.session.begin_nested():
            db.session.delete(obj)

    @classmethod
    def get(cls, id):
        if obj := db.session.get(cls, id):
            return obj

        raise NotExistsError(id)


class NotifyInboxModel(db.Model, Timestamp, DbOperationMixin):
    __tablename__ = "notify_inbox"

    id = db.Column(db.Integer, primary_key=True)

    raw = db.Column(db.Text, nullable=False)
    """ Coar notification data as json string """

    record_id = db.Column(db.Text, nullable=False)

    process_date = db.Column(db.DateTime, nullable=True)

    @classmethod
    def create(cls, data):
        with db.session.begin_nested():
            obj = cls(
                raw=data.get("raw"),
                record_id=data.get("record_id"),
            )
            db.session.add(obj)

        return obj

    @classmethod
    def search(cls, search_params=None, filters=None):
        query = db.session.query(NotifyInboxModel)
        if filters:
            results = query.filter(or_(*filters))
        else:
            results = query.filter()

        return results


class EndorsementMetadataModel(db.Model, RecordMetadataBase, DbOperationMixin):
    __tablename__ = "endorsement_metadata"

    def create(self):
        with db.session.begin_nested():
            db.session.add(self)
