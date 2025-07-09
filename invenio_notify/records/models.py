from typing import Iterable

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy import or_
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import Timestamp
from sqlalchemy_utils.types import JSONType, UUIDType

from invenio_notify import constants
from invenio_notify.errors import NotExistsError
from invenio_rdm_records.records.models import RDMRecordMetadata, RDMParentMetadata

JSON = (
    db.JSON()
    .with_variant(postgresql.JSONB(none_as_null=True), "postgresql")
    .with_variant(JSONType(), "sqlite")
    .with_variant(JSONType(), "mysql")
)


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

    @classmethod
    def update(cls, data, id):
        with db.session.begin_nested():
            # NOTE:
            # with db.session.get(cls, id) the model itself would be
            # returned and this classmethod would be called
            db.session.query(cls).filter_by(id=id).update(data)


class NotifyInboxModel(db.Model, Timestamp, DbOperationMixin):
    __tablename__ = "notify_inbox"

    id = db.Column(db.Integer, primary_key=True)

    # TODO somehow it can be other value than UUIDType, change it to string
    noti_id = db.Column(UUIDType, nullable=False, unique=True)
    """ notification id from COAR notification """

    raw = db.Column(JSON, nullable=False)
    """ Coar notification data as json string """

    recid = db.Column(db.Text, nullable=False)
    """ record id (recid e.g. p97a0-c4p20 ) instead of uuid of record """

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
    """ user id of the sender """

    @classmethod
    def unprocessed_records(cls) -> Iterable["NotifyInboxModel"]:
        """Get all unprocessed inbox records (where process_date is None)."""
        return cls.search(None, [cls.process_date.is_(None)])


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

    reviewer_id = db.Column(
        db.Integer(),
        db.ForeignKey("reviewer.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reviewer = db.relationship(
        "ReviewerModel", backref=db.backref("member_mappings", cascade="all, delete-orphan")
    )

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


class ReviewerModel(db.Model, Timestamp, DbOperationMixin):
    __tablename__ = "reviewer"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False)

    actor_id = db.Column(db.Text, nullable=True, unique=True)
    """ id that used in COAR notification (json) """

    inbox_url = db.Column(db.Text, nullable=True)

    inbox_api_token = db.Column(db.Text, nullable=True)

    description = db.Column(db.Text, nullable=True)

    members = db.relationship(
        "User",
        secondary=ReviewerMapModel.__tablename__,
    )

    endorsements = db.relationship("EndorsementModel", back_populates="reviewer")

    @classmethod
    def has_member_with_email(cls, email, actor_id) -> bool:
        """Check if a user with given email is a member of a reviewer with the given actor_id.
        
        Args:
            email: Email address of the user
            actor_id: The actor_id of the reviewer
            
        Returns:
            bool: True if the user is a member of the reviewer, False otherwise
        """
        result = (db.session.query(cls)
                  .join(ReviewerMapModel, ReviewerMapModel.reviewer_id == cls.id)
                  .join(User, User.id == ReviewerMapModel.user_id)
                  .filter(User.email == email, cls.actor_id == actor_id)
                  .first())
        return result is not None

    @classmethod
    def has_member(cls, user_id, actor_id) -> bool:
        """Check if a user with given user_id is a member of a reviewer with the given actor_id.
        
        Args:
            user_id: ID of the user
            actor_id: The actor_id of the reviewer
            
        Returns:
            bool: True if the user is a member of the reviewer, False otherwise
        """
        result = (db.session.query(cls)
                  .join(ReviewerMapModel, ReviewerMapModel.reviewer_id == cls.id)
                  .filter(ReviewerMapModel.user_id == user_id, cls.actor_id == actor_id)
                  .first())
        return result is not None


class EndorsementModel(db.Model, Timestamp, DbOperationMixin):
    __tablename__ = "endorsement"

    id = db.Column(db.Integer, primary_key=True)

    record_id = db.Column(UUIDType, db.ForeignKey(
        RDMRecordMetadata.id, ondelete="CASCADE",
    ), index=True, nullable=True, )

    parent_id = db.Column(UUIDType, db.ForeignKey(
        RDMParentMetadata.id, ondelete="CASCADE",
    ), index=True, nullable=True, )

    record = db.relationship(RDMRecordMetadata, foreign_keys=[record_id])
    """ id of the record, id that save in postgres instead of recid that used in json and /records  """

    reviewer_id = db.Column(
        db.Integer,
        db.ForeignKey("reviewer.id", ondelete="NO ACTION"),
        nullable=True,
        index=True,
    )
    """ id of Review service provider (e.g. id of PCI) """
    reviewer = db.relationship("ReviewerModel", back_populates="endorsements")

    review_type = db.Column(db.Text, nullable=True)
    """ review or endorsement """

    inbox_id = db.Column(db.Integer, db.ForeignKey(
        NotifyInboxModel.id, ondelete="SET NULL"
    ), nullable=True, unique=True)
    inbox = db.relationship(NotifyInboxModel, foreign_keys=[inbox_id], uselist=False)

    result_url = db.Column(db.Text, nullable=False)
    """ url of review results """

    reviewer_name = db.Column(db.Text, nullable=False)
    """ name of the reviewer, copy it in case the reviewer is deleted """

    endorsement_reply_id = db.Column(
        db.Integer,
        db.ForeignKey("endorsement_reply.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    endorsement_reply = db.relationship("EndorsementReplyModel", uselist=False)


class EndorsementRequestModel(db.Model, Timestamp, DbOperationMixin):
    """
    This model stores records created by record owners who want to send endorsement requests to reviewers.
    It serves as an outbox of our repository system for COAR endorsement notifications.
    """
    __tablename__ = "endorsement_request"

    id = db.Column(db.Integer, primary_key=True)

    noti_id = db.Column(UUIDType, nullable=False, unique=True)
    """ notification id from COAR notification """

    record_id = db.Column(UUIDType, db.ForeignKey(
        RDMRecordMetadata.id, ondelete="NO ACTION",
    ), index=True, nullable=False)
    """ record uuid that binded to version """

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    """ user id of the sender """

    reviewer_id = db.Column(
        db.Integer,
        db.ForeignKey("reviewer.id", ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    reviewer = db.relationship("ReviewerModel")

    raw = db.Column(JSON, nullable=False)
    """ raw notification data as json """

    latest_status = db.Column(db.Text, nullable=False)
    """ latest status e.g 'Request Endorsement', 'Reject', 'Announce Endorsement' """

    replies = db.relationship("EndorsementReplyModel", back_populates="endorsement_request")

    @classmethod
    def update_latest_status_by_request_id(cls, endorsement_request_id):
        if not endorsement_request_id:
            return None

        # Get the latest status from endorsement_reply using the endorsement_request_id
        latest_status = (EndorsementReplyModel.query
                         .with_entities(EndorsementReplyModel.status)
                         .filter_by(endorsement_request_id=endorsement_request_id)
                         .order_by(EndorsementReplyModel.created.desc())
                         .limit(1)
                         .scalar())

        latest_status = latest_status or constants.STATUS_REQUEST_ENDORSEMENT

        cls.update({'latest_status': latest_status}, endorsement_request_id)
        return latest_status


class EndorsementReplyModel(db.Model, Timestamp, DbOperationMixin):
    __tablename__ = "endorsement_reply"

    id = db.Column(db.Integer, primary_key=True)

    endorsement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("endorsement_request.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    endorsement_request = db.relationship("EndorsementRequestModel", back_populates="replies")

    inbox_id = db.Column(
        db.Integer,
        db.ForeignKey(NotifyInboxModel.id, ondelete="SET NULL"),
        nullable=True,
        index=True,
        unique=True,
    )
    inbox = db.relationship(NotifyInboxModel, uselist=False)

    status = db.Column(db.Text, nullable=False)
    """ status e.g 'Request Endorsement', 'Reject', 'Announce Endorsement' """

    message = db.Column(db.Text, nullable=True)
    """ message of the reply, can be empty if no message """
