from invenio_records_resources.services.records.results import RecordItem
from invenio_pidstore.errors import PIDDoesNotExistError

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.models import RDMRecordMetadata


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

def get_recid_by_record_uuid(record_uuid: str) -> str:

    recid = (RDMRecordMetadata.query
              .filter_by(id=record_uuid)
              .with_entities(RDMRecordMetadata.json.op("->>")('id')).scalar())
    return recid


def get_rdm_record_by_uuid(record_uuid: str) -> RDMRecord:
    recid = get_recid_by_record_uuid(record_uuid)
    return resolve_record_from_pid(recid)
