from typing import List, Dict

from flask import current_app

from invenio_notify import constants
from invenio_notify.records.models import EndorsementModel
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

        # Get all endorsements for this parent's children
        endorsements = EndorsementModel.query_by_parent_id(parent_id).all()

        if not endorsements:
            return []

        actor_endorsements = {}
        for endorsement in endorsements:
            actor_id = endorsement.actor_id
            if actor_id not in actor_endorsements:
                actor_endorsements[actor_id] = {
                    'endorsements': [],
                    'reviews': []
                }

            if endorsement.review_type == constants.TYPE_ENDORSEMENT:
                actor_endorsements[actor_id]['endorsements'].append(endorsement)
            elif endorsement.review_type == constants.TYPE_REVIEW:
                actor_endorsements[actor_id]['reviews'].append(endorsement)
            else:
                current_app.logger.warning(
                    f'Unknown review type: {endorsement.review_type} for endorsement {endorsement.id}')

        result = []
        for actor_id, data in actor_endorsements.items():
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
            actor_name = _endorsements[-1].actor.name if _endorsements else 'Unknown'
            result.append({
                'actor_id': actor_id,
                'actor_name': actor_name,
                'endorsement_count': len(sub_endorsement_list),
                'review_count': len(sub_review_list),
                'endorsement_list': sub_endorsement_list,
                'review_list': sub_review_list,
            })

        return result

    @staticmethod
    def get_notify_info(parent_id) -> Dict:
        """
        designed for indexing and used by dumper on invenio-rdm-records
        notify field contain information of notify for search purpose
        """
        return {
            'has_reviews': EndorsementModel.query_by_parent_id(parent_id).count() > 0
        }
