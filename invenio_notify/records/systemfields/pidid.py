from invenio_db import db
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records.systemfields import SystemField, SystemFieldContext
from invenio_records_resources.records.api import PersistentIdentifierWrapper
from uuid import UUID

PID_TYPE_ENDORSEMENT = 'endorsement'


class PIDIdOnlyFieldContext(SystemFieldContext):
    def __init__(self, *args, pid_type=None, **kwargs):
        super(PIDIdOnlyFieldContext, self).__init__(*args, **kwargs)
        self._pid_type = pid_type

    def parse_pid(self, value):
        """Parse pid."""
        if isinstance(value, UUID):
            return value
        try:
            return UUID(value)
        except (TypeError, ValueError):
            return value

    def resolve(self, pid_value):
        """Resolve identifier (either uuid)."""
        pid_value = self.parse_pid(pid_value)

        field_name = self.field._id_field
        if not pid_value:
            raise PIDDoesNotExistError(self._pid_type, "")

        with db.session.no_autoflush:  # avoid flushing the current session
            model = self.record_cls.model_cls.query.filter_by(
                **{field_name: pid_value}
            ).one_or_none()
            if model is None:
                raise PIDDoesNotExistError(self._pid_type, str(pid_value))
            record = self.record_cls(model.data, model=model)
            if record.is_deleted:
                raise PIDDeletedError(PersistentIdentifierWrapper(pid_value), record)
            return record


class PIDIdOnlyField(SystemField):
    """System field for managing record access."""

    def __init__(self, id_field, pid_type):
        """Create a new RecordAccessField instance."""
        self._id_field = id_field
        self._pid_type = pid_type

    def obj(self, record):
        """Get the access object."""
        pid_value = getattr(record, self._id_field)
        if pid_value is None:
            return None
        return PersistentIdentifierWrapper(str(pid_value))

    def __get__(self, record, owner=None):
        """Get the record's access object."""
        if record is None:
            # access by class
            return PIDIdOnlyFieldContext(self, owner, pid_type=self._pid_type)

        # access by object
        return self.obj(record)

    #
    # Life-cycle hooks
    #
    def pre_commit(self, record):
        """Called before a record is committed."""
        # Make sure we don't dump the two model fields into the JSON of the
        # record.
        record.pop(self._id_field, None)
