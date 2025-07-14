from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service


def resolve_record_from_pid(pid_value):
    """Resolve a record from its PID value.
    
    Args:
        pid_value: The record PID value (e.g., 'xxxx-xxxx')
        
    Returns:
        RDMRecord: The resolved record object
        
    Raises:
        PIDDoesNotExistError: If the PID doesn't exist
    """
    return current_rdm_records_service.record_cls.pid.resolve(pid_value, registered_only=False)