from invenio_accounts.models import User
from invenio_db import db
from invenio_rdm_records.records.models import RDMRecordMetadata
from invenio_records.models import RecordMetadataBase
from sqlalchemy import or_
from sqlalchemy_utils import UUIDType
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

    @classmethod
    def create(cls, data):
        with db.session.begin_nested():
            obj = cls(
                **data
            )
            db.session.add(obj)

        return obj

    @classmethod
    def search(cls, search_params=None, filters=None):
        query = db.session.query(cls)
        if filters:
            results = query.filter(or_(*filters))
        else:
            results = query.filter()

        return results


class NotifyInboxModel(db.Model, Timestamp, DbOperationMixin):
    __tablename__ = "notify_inbox"

    id = db.Column(db.Integer, primary_key=True)

    raw = db.Column(db.Text, nullable=False)
    """ Coar notification data as json string """

    recid = db.Column(db.Text, nullable=False)
    """ record id (recid) instead of object id of record """

    process_date = db.Column(db.DateTime, nullable=True)

    process_note = db.Column(db.Text, nullable=True, )
    """ additional note (such as error message) after processed """

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )

    user = db.relationship(
        "User", backref=db.backref("inbox_messages", cascade="all, delete-orphan")
    )


class ReviewerMapModel(db.Model, Timestamp, DbOperationMixin):
    """
    used to store mapping between user and actor id

    prevent user to send notification with different actor id
    """

    __tablename__ = "reviewer_map"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user = db.relationship(
        "User", backref=db.backref("reviewer_ids", cascade="all, delete-orphan")
    )

    reviewer_id = db.Column(db.Text, nullable=False)
    """ ID of the reviewer in an external system, in COAR this is the actor.id """

    @classmethod
    def find_by_email(cls, email):
        return (cls.query
                .join(User, cls.user_id == User.id)
                .filter(User.email == email)
                .all())

    @classmethod
    def find_by_reviewer_id(cls, reviewer_id):
        return cls.query.filter(cls.reviewer_id == reviewer_id).all()

    @classmethod
    def find_review_id_by_user_id(cls, user_id):
        """ find list of reviewer_id by user_id """
        return [r[0] for r in db.session.query(cls.reviewer_id).filter(cls.user_id == user_id).all()]


class EndorsementMetadataModel(db.Model, RecordMetadataBase, DbOperationMixin):
    __tablename__ = "endorsement_metadata"

    record_id = db.Column(UUIDType, db.ForeignKey(
        RDMRecordMetadata.id, ondelete="CASCADE",
    ), index=True, nullable=True, )

    record = db.relationship(RDMRecordMetadata, foreign_keys=[record_id])
    """ id of the record, id that save in postgres instead of recid that used in json and /records  """

    reviewer_id = db.Column(db.Text, nullable=True)
    """ id of Review service provider (e.g. id of PCI) """
    # TOBE to be defined contain of reviewer_id

    review_type = db.Column(db.Text, nullable=True)
    """ review or endorsement """

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="NO ACTION"),
        nullable=True,
        index=True,
    )
    """ user id of the sender """

    inbox_id = db.Column(db.Integer, db.ForeignKey(
        NotifyInboxModel.id, ondelete="NO ACTION"
    ), nullable=True)
    inbox = db.relationship(NotifyInboxModel, foreign_keys=[inbox_id])

    def create(self):
        with db.session.begin_nested():
            db.session.add(self)
