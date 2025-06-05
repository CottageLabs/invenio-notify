"""System field for counting endorsements of a record."""

from invenio_records.systemfields import SystemField

from invenio_notify.proxies import current_endorsement_service


def get_with_cache(field: SystemField, record, get_fn):
    if record is None:
        return field

    value = field._get_cache(record)
    if value is not None:
        return value

    value = get_fn(record)
    field._set_cache(record, value)
    return value


class EndorsementListField(SystemField):
    """System field for accessing the number of endorsements for a record."""

    def __init__(self, key=None):
        """Constructor."""
        super().__init__(key=key)

    def get_no_cache(self, record):
        endorsements = current_endorsement_service.get_endorsement_info(record.id)
        return endorsements

    def __get__(self, record, owner=None):
        """Get the endorsement information."""
        return get_with_cache(self, record, self.get_no_cache)

    def pre_commit(self, record):
        """Dump the endorsement information before committing the record."""
        record[self.key] = self.__get__(record)
