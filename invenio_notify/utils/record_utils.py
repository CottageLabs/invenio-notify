from invenio_records_resources.services.records.results import RecordItem

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records import RDMRecord


def resolve_record_from_pid(pid_value) -> RDMRecord:
    """Resolve a record from its PID value.
    
    Args:
        pid_value: The record PID value (e.g., 'xxxx-xxxx')
        
    Returns:
        RDMRecord: The resolved record object
        
    Raises:
        PIDDoesNotExistError: If the PID doesn't exist
    """
    return current_rdm_records_service.record_cls.pid.resolve(pid_value, registered_only=False)


def read_record_item(*args, **kwargs) -> RecordItem:
    return current_rdm_records_service.read(*args, **kwargs)
