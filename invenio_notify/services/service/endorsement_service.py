from typing import List, Dict

from flask import current_app
from invenio_db import db
from sqlalchemy.orm import selectinload

from invenio_notify import constants
from invenio_notify.records.models import EndorsementModel
from invenio_rdm_records.records.models import RDMRecordMetadata
from .base_service import BasicDbService


class EndorsementAdminService(BasicDbService):
    """Service for managing endorsements."""

    @staticmethod
    def get_endorsement_info(parent_id) -> List[Dict]:
        """Get the endorsement information for a record by its parent ID.
        Note: This method is not actually called in this module, it is called in
        InvenioRDMRecords by the EndorsementsDumperExt and as a backup for the
        Endorsements system field getter.

        Args:
            parent_id: The UUID of the record
            
        Returns:
            list: A list of dictionaries containing endorsement information
        """
        if not parent_id:
            return []

        # Get all child record IDs for this parent
        child_record_ids = [row[0] for row in
                            db.session.query(RDMRecordMetadata.id).filter_by(parent_id=parent_id).all()]

        # Query endorsements for any of the child records
        endorsements = (
            db.session.query(EndorsementModel)
            .options(selectinload(EndorsementModel.record))
            .filter(EndorsementModel.record_id.in_(child_record_ids))
            .all()
        )

        if not endorsements:
            return []

        reviewer_endorsements = {}
        for endorsement in endorsements:
            reviewer_id = endorsement.reviewer_id
            if reviewer_id not in reviewer_endorsements:
                reviewer_endorsements[reviewer_id] = {
                    'endorsements': [],
                    'reviews': []
                }

            if endorsement.review_type == constants.TYPE_ENDORSEMENT:
                reviewer_endorsements[reviewer_id]['endorsements'].append(endorsement)
            elif endorsement.review_type == constants.TYPE_REVIEW:
                reviewer_endorsements[reviewer_id]['reviews'].append(endorsement)
            else:
                current_app.logger.warning(
                    f'Unknown review type: {endorsement.review_type} for endorsement {endorsement.id}')

        result = []
        for reviewer_id, data in reviewer_endorsements.items():
            sub_endorsement_list = []
            sub_review_list = []

            for e in data['endorsements']:
                sub_endorsement_list.append({
                    'created': e.created.isoformat(),
                    'url': e.result_url,
                    'index': e.record.index
                })

            for r in data['reviews']:
                sub_review_list.append({
                    'created': r.created.isoformat(),
                    'url': r.result_url,
                    'index': r.record.index
                })

            _endorsements = data['reviews'] + data['endorsements']
            reviewer_name = _endorsements[-1].reviewer.name if _endorsements else 'Unknown'
            result.append({
                'reviewer_id': reviewer_id,
                'reviewer_name': reviewer_name,
                'endorsement_count': len(sub_endorsement_list),
                'review_count': len(sub_review_list),
                'endorsement_list': sub_endorsement_list,
                'review_list': sub_review_list,
            })

        return result