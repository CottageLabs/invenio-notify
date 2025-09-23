from typing import Iterable

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy import and_, or_, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import selectinload
from sqlalchemy_utils.types import JSONType, UUIDType, URLType

from invenio_notify import constants
from invenio_notify.constants import WORKFLOW_STATUS_AVAILABLE
from invenio_notify.errors import NotExistsError
from invenio_notify.records.mixins import UTCTimestamp
from invenio_rdm_records.records.models import RDMRecordMetadata

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
        
        # Apply search filters
        if filters:
            for filter_condition in filters:
                query = query.filter(filter_condition)
        
        # Apply sorting if specified
        if search_params and "sort" in search_params:
            sort_fields = search_params["sort"]
            sort_direction_func = search_params.get("sort_direction")
            
            # Handle sort_fields as list (from map_search_params)
            if isinstance(sort_fields, list) and sort_fields:
                sort_field = sort_fields[0]  # Use first field for sorting
            elif isinstance(sort_fields, str):
                sort_field = sort_fields
            else:
                sort_field = None
            
            if sort_field:
                # Handle minus-prefixed sort fields (e.g., "-created" for descending)
                if sort_field.startswith('-'):
                    actual_field = sort_field[1:]  # Remove minus prefix
                    is_descending = True
                else:
                    actual_field = sort_field
                    is_descending = False
                
                if hasattr(cls, actual_field):
                    column = getattr(cls, actual_field)
                    
                    # Apply sorting direction
                    if is_descending:
                        query = query.order_by(column.desc())
                    elif callable(sort_direction_func):
                        # Use the SQLAlchemy function if provided
                        query = query.order_by(sort_direction_func(column))
                    else:
                        query = query.order_by(column.asc())
        
        # Apply pagination if specified
        if search_params:
            page = search_params.get("page", 1)
            size = search_params.get("size", 25)
            
            # Calculate offset
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)

        return query

    @classmethod
    def update(cls, data, id):
        with db.session.begin_nested():
            # NOTE:
            # with db.session.get(cls, id) the model itself would be
            # returned and this classmethod would be called
            db.session.query(cls).filter_by(id=id).update(data)


class NotifyInboxModel(db.Model, UTCTimestamp, DbOperationMixin):
    """
    Stores all valid COAR notifications from the inbox endpoint.
    """
    __tablename__ = "notify_inbox"

    id = db.Column(db.Integer, primary_key=True)

    notification_id = db.Column(db.Text, nullable=False, unique=True)
    """ Notification ID from the COAR notification """

    raw = db.Column(JSON, nullable=False)
    """ COAR notification data as a JSON string """

    record_id = db.Column(db.Text, nullable=False)
    """ Record ID (e.g. p97a0-c4p20) instead of UUID of the record """

    process_date = db.Column(db.DateTime, nullable=True)

    process_note = db.Column(db.Text, nullable=True)
    """ An additional note (such as error message) after processing """

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    user = db.relationship(
        "User", backref=db.backref("inbox_messages", cascade="all, delete-orphan")
    )
    """ User ID of the sender """

    @classmethod
    def unprocessed_records(cls, batch_size=100) -> Iterable["NotifyInboxModel"]:
        """Generator that yields batches of unprocessed inbox records.

        Args:
            batch_size: Number of records per batch (default: 100)

        Yields:
            List of NotifyInboxModel instances (up to batch_size per batch)
        """
        offset = 0
        while True:
            query = cls.query.filter(cls.process_date.is_(None))
            batch = query.offset(offset).limit(batch_size).all()
            if not batch:
                break
            for r in batch:
                yield r
            offset += batch_size


class ActorMapModel(db.Model, UTCTimestamp, DbOperationMixin):
    """ Used to store actor membership mappings. """

    __tablename__ = "actor_map"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user = db.relationship(
        "User", backref=db.backref("actor_ids", cascade="all, delete-orphan")
    )

    actor_id = db.Column(
        db.Integer(),
        db.ForeignKey("notify_actor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    actor = db.relationship(
        "ActorModel", backref=db.backref("member_mappings", cascade="all, delete-orphan")
    )

    @classmethod
    def find_by_email(cls, email):
        return (cls.query
                .join(User, cls.user_id == User.id)
                .filter(User.email == email)
                .all())

    @classmethod
    def find_by_actor_id(cls, actor_id):
        return cls.query.filter(cls.actor_id == actor_id).all()

    @classmethod
    def find_review_id_by_user_id(cls, user_id):
        """ Find a list of actor IDs by user ID. """
        return [r[0] for r in db.session.query(cls.actor_id).filter(cls.user_id == user_id).all()]


class ActorModel(db.Model, UTCTimestamp, DbOperationMixin):
    """
    An organization that provides a review service, e.g. PCI, COAR, etc.

    If inbox_url, inbox_api_token is set, it will allow Record owners to send endorsement requests.
    """
    __tablename__ = "notify_actor"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False)

    actor_id = db.Column(db.Text, nullable=True, unique=True)
    """ ID that is used in COAR notification (JSON) """

    inbox_url = db.Column(URLType, nullable=True)

    inbox_api_token = db.Column(db.Text, nullable=True)

    description = db.Column(db.Text, nullable=True)

    members = db.relationship(
        "User",
        secondary=ActorMapModel.__tablename__,
    )

    endorsements = db.relationship("EndorsementModel", back_populates="actor")

    @classmethod
    def has_member_with_email(cls, email, actor_id) -> bool:
        """Check if a user with given email is a member of a actor with the given actor_id.
        
        Args:
            email: Email address of the user
            actor_id: The actor_id of the actor
            
        Returns:
            bool: True if the user is a member of the actor, False otherwise
        """
        result = (db.session.query(cls)
                  .join(ActorMapModel, ActorMapModel.actor_id == cls.id)
                  .join(User, User.id == ActorMapModel.user_id)
                  .filter(User.email == email, cls.actor_id == actor_id)
                  .first())
        return result is not None

    @classmethod
    def has_member(cls, user_id, actor_id) -> bool:
        """Check if a user with given user_id is a member of a actor with the given actor_id.
        
        Args:
            user_id: ID of the user
            actor_id: The actor_id of the actor
            
        Returns:
            bool: True if the user is a member of the actor, False otherwise
        """
        result = (db.session.query(cls)
                  .join(ActorMapModel, ActorMapModel.actor_id == cls.id)
                  .filter(ActorMapModel.user_id == user_id, cls.actor_id == actor_id)
                  .first())
        return result is not None

    @classmethod
    def has_available_actors(cls, record_id) -> bool:
        """Check if there are any available actors for endorsement requests.
        
        Args:
            record_id: UUID of the record
            
        Returns:
            bool: True if there are available actors, False otherwise
        """
        
        # Check if any actors exist with required configuration
        configured_actors_exist = (
            db.session.query(cls.id)
            .filter(
                and_(
                    cls.inbox_url.isnot(None),
                    cls.inbox_api_token.isnot(None),
                    cls.inbox_url != '',
                    cls.inbox_api_token != ''
                )
            )
            .first()
        )
        
        if not configured_actors_exist:
            return False
        
        # For each configured actor, check if they are available for this record
        # An actor is available if:
        # 1. No endorsement exists for this record+actor, OR
        # 2. No endorsement request exists for this record+actor, OR  
        # 3. Latest endorsement request status is TYPE_TENTATIVE_REJECT
        
        configured_actor_ids = (
            db.session.query(cls.id)
            .filter(
                and_(
                    cls.inbox_url.isnot(None),
                    cls.inbox_api_token.isnot(None),
                    cls.inbox_url != '',
                    cls.inbox_api_token != ''
                )
            )
            .subquery()
        )
        
        # Check if there's at least one actor that is available
        # An actor is available if:
        # 1. No endorsement exists for that record+actor AND
        # 2. Either no endorsement request exists OR endorsement request has TYPE_TENTATIVE_REJECT
        available_actor = (
            db.session.query(configured_actor_ids.c.id)
            .outerjoin(
                EndorsementModel,
                and_(
                    EndorsementModel.actor_id == configured_actor_ids.c.id,
                    EndorsementModel.record_id == record_id
                )
            )
            .outerjoin(
                EndorsementRequestModel,
                and_(
                    EndorsementRequestModel.actor_id == configured_actor_ids.c.id,
                    EndorsementRequestModel.record_id == record_id
                )
            )
            .filter(
                and_(
                    # No endorsement exists
                    EndorsementModel.id.is_(None),
                    # AND either no endorsement request exists OR it has tentative reject status
                    or_(
                        EndorsementRequestModel.id.is_(None),
                        EndorsementRequestModel.latest_status == constants.WORKFLOW_STATUS_TENTATIVE_REJECT
                    )
                )
            )
            .first()
        )
        
        return available_actor is not None

    @classmethod
    def get_available_actors(cls, record_id):
        """Get list of all actors that:
              1. Have inbox_url configured
              2. Have inbox_api_token configured
              3. inbox_url is not empty
              4. inbox_api_token is not empty
              5. Either have no endorsements OR have endorsements that aren't completed types
        
        Args:
            record_id: UUID of the record
            
        Returns:
            list: List of actor dictionaries with actor_id, actor_name, and status
        """
        
        # Get all actors with inbox configuration and their endorsement/request statuses
        query = (
            db.session.query(
                cls.id.label('actor_id'),
                cls.name.label('actor_name'),
                cls.inbox_url,
                cls.inbox_api_token,
                # Get latest endorsement status
                func.max(EndorsementModel.review_type).label('endorsement_status'),
                # Get latest endorsement request status
                func.max(EndorsementRequestModel.latest_status).label('request_status')
            )
            .outerjoin(
                EndorsementModel,
                and_(
                    EndorsementModel.actor_id == cls.id,
                    EndorsementModel.record_id == record_id
                )
            )
            .outerjoin(
                EndorsementRequestModel,
                and_(
                    EndorsementRequestModel.actor_id == cls.id,
                    EndorsementRequestModel.record_id == record_id
                )
            )
            # Filter for actors with required inbox configuration
            .filter(
                and_(
                    cls.inbox_url.isnot(None),
                    cls.inbox_api_token.isnot(None),
                    cls.inbox_url != '',
                    cls.inbox_api_token != '',
                    # Exclude actors who have completed endorsements/reviews for this record
                    or_(
                        EndorsementModel.review_type.is_(None),
                        EndorsementModel.review_type.notin_([constants.TYPE_REVIEW, constants.TYPE_ENDORSEMENT])
                    )
                )
            )
            .group_by(cls.id, cls.name, cls.inbox_url, cls.inbox_api_token)
        )
        
        results = query.all()
        actors = []
        
        for result in results:
            # Determine status based on endorsement and request states
            if result.endorsement_status:
                # If there's an endorsement, use that status
                status = result.endorsement_status
            elif result.request_status:
                # The latest request status is updated when a reply is received
                status = result.request_status
            else:
                # No request or endorsement, actor is available
                status = WORKFLOW_STATUS_AVAILABLE

            actors.append({
                "actor_id": result.actor_id,
                "actor_name": result.actor_name,
                "status": status,
            })
        
        return actors


class EndorsementModel(db.Model, UTCTimestamp, DbOperationMixin):
    """
    Endorsement data for the record

    Both Review and Endorsement records from Actor will be stored here.
    """

    __tablename__ = "endorsement"

    id = db.Column(db.Integer, primary_key=True)

    record_id = db.Column(UUIDType, db.ForeignKey(
        RDMRecordMetadata.id, ondelete="CASCADE",
    ), index=True, nullable=True, )

    record = db.relationship(RDMRecordMetadata, foreign_keys=[record_id])
    """ ID of the record, ID that is saved in PostgreSQL instead of recid that is used in JSON and /records """

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey("notify_actor.id", ondelete="NO ACTION"),
        nullable=True,
        index=True,
    )
    """ ID of review service provider (e.g. ID of PCI) """
    actor = db.relationship("ActorModel", back_populates="endorsements")

    review_type = db.Column(db.Text, nullable=True)
    """ review or endorsement """

    inbox_id = db.Column(db.Integer, db.ForeignKey(
        NotifyInboxModel.id, ondelete="SET NULL"
    ), nullable=True, unique=True)
    inbox = db.relationship(NotifyInboxModel, foreign_keys=[inbox_id], uselist=False)

    result_url = db.Column(db.Text, nullable=False)
    """ URL of review results """

    actor_name = db.Column(db.Text, nullable=False)
    """ Name of the actor; copied in case the actor is deleted """

    endorsement_reply_id = db.Column(
        db.Integer,
        db.ForeignKey("endorsement_reply.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    endorsement_reply = db.relationship("EndorsementReplyModel", uselist=False)

    @classmethod
    def get_latest_status(cls, record_id, actor_id):
        """Get latest endorsement status for record and actor."""
        return (
            cls.query.filter_by(
                record_id=record_id,
                actor_id=actor_id,
            )
            .order_by(cls.created.desc())
            .with_entities(cls.review_type)
            .limit(1)
            .scalar()
        )

    @classmethod
    def query_by_parent_id(cls, parent_id):
        """Get all endorsements for a parent's children.

        Args:
            parent_id: The UUID of the parent record

        Returns:
            Query result of all endorsements for the parent's children
        """
        return (
            db.session.query(cls)
            .join(RDMRecordMetadata, cls.record_id == RDMRecordMetadata.id)
            .options(selectinload(cls.record))
            .filter(RDMRecordMetadata.parent_id == parent_id)
        )


class EndorsementRequestModel(db.Model, UTCTimestamp, DbOperationMixin):
    """
    Endorsement Request that is sent by record owners to actors.

    It serves as an outbox of our repository system for COAR endorsement notifications.
    """
    __tablename__ = "endorsement_request"

    id = db.Column(db.Integer, primary_key=True)

    notification_id = db.Column(db.Text, nullable=False, unique=True)
    """ Notification ID from the COAR notification """

    record_id = db.Column(UUIDType, db.ForeignKey(
        RDMRecordMetadata.id, ondelete="NO ACTION",
    ), index=True, nullable=False)
    """ Record UUID that is bound to a version """

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey(User.id, ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    """ User ID of the sender """

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey("notify_actor.id", ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    actor = db.relationship("ActorModel")

    raw = db.Column(JSON, nullable=False)
    """ Raw notification data as JSON """

    latest_status = db.Column(db.Text, nullable=False)
    """ Latest status, e.g., 'coar-notify:EndorsementAction', 'Request Endorsement', 'Reject', 'Announce Endorsement'
        This field is updated when a reply is received."""

    replies = db.relationship("EndorsementReplyModel", back_populates="endorsement_request")

    @classmethod
    def get_latest_status(cls, record_id, actor_id, include_id=False):
        """Get latest endorsement request status for record and actor.
        
        Args:
            record_id: UUID of the record
            actor_id: ID of the actor
            include_id: If True, returns (status, notification_id) tuple
            
        Returns:
            str: latest status if include_notification_id=False
            tuple: (status, notification_id) if include_notification_id=True
            None: if no request found
        """
        query = (
            cls.query.filter_by(
                record_id=record_id,
                actor_id=actor_id,
            )
            .order_by(cls.created.desc())
            .limit(1)
        )
        
        if include_id:
            result = query.with_entities(cls.latest_status, cls.notification_id).first()
            return result if result else (None, None)
        else:
            return query.with_entities(cls.latest_status).scalar()

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

        latest_status = latest_status or constants.WORKFLOW_STATUS_REQUEST_ENDORSEMENT

        cls.update({'latest_status': latest_status}, endorsement_request_id)
        return latest_status


class EndorsementReplyModel(db.Model, UTCTimestamp, DbOperationMixin):
    """
    Stores replies to EndorsementRequestModel.

    Only stores records where a notification is `inReplyTo` a notification from EndorsementRequestModel.
    Notifications that are not a reply to an endorsement request will not be stored here.
    """

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
    """ Status, e.g., 'Request Endorsement', 'Reject', 'Announce Endorsement' """

    message = db.Column(db.Text, nullable=True)
    """ Message of the reply, can be empty """
