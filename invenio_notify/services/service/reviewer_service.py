from flask import current_app
from invenio_accounts.models import User
from invenio_db.uow import unit_of_work
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper

from invenio_notify.records.models import ReviewerMapModel, ReviewerModel
from invenio_notify.utils import user_utils, reviewer_utils
from .base_service import BasicDbService


class ReviewerService(BasicDbService):
    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        if filter_maker is None:
            def filter_maker(query_param):
                filters = []
                if query_param:
                    filters.extend([
                        self.record_cls.name.ilike(f'%{query_param}%'),
                    ])
                return filters

        return super().search(identity, params, search_preference, expand, filter_maker, **kwargs)

    @property
    def schema_add_member(self):
        return ServiceSchemaWrapper(self, schema=self.config.schema_add_member)

    @property
    def schema_del_member(self):
        return ServiceSchemaWrapper(self, schema=self.config.schema_del_member)

    def add_member(self, identity, id, data, raise_errors=True):
        self.require_permission(identity, "update")

        valid_data, errors = self.schema_add_member.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        return self.add_member_by_emails(id, valid_data['emails'])

    @unit_of_work()
    def add_member_by_emails(self, reviewer_id, emails, uow=None):
        reviewer: ReviewerModel = self.record_cls.get(reviewer_id)

        new_emails = set(emails)
        existing_emails = {m.email for m in reviewer.members}
        duplicate_emails = new_emails.intersection(existing_emails)
        if duplicate_emails:
            current_app.logger.info(f'Emails already exist: {duplicate_emails}')

        new_emails = new_emails - existing_emails
        if not new_emails:
            current_app.logger.info('No new emails to add')
            raise ValueError('Duplicate emails found')

        for email in new_emails:
            user = user_utils.find_user_by_email(email)
            if user:
                current_app.logger.info(f'Adding user [{user.email}] to reviewer [{reviewer.actor_id}]')
                reviewer_utils.add_member_to_reviewer(reviewer_id, user.id, uow=uow)
            else:
                current_app.logger.warning(f'User with email {email} not found')

        reviewer = self.record_cls.get(reviewer_id)
        return reviewer

    def del_member(self, identity, id, data, raise_errors=True):
        self.require_permission(identity, "update")

        valid_data, errors = self.schema_del_member.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        return self.del_member_by_id(id, valid_data['user_id'])

    @unit_of_work()
    def del_member_by_id(self, reviewer_id, user_id, uow=None):
        reviewer: ReviewerModel = self.record_cls.get(reviewer_id)
        user: User = User.query.get(user_id)

        if user not in reviewer.members:
            current_app.logger.info(f'User [{user.email}] is not a member of reviewer [{reviewer.actor_id}]')
            return reviewer

        current_app.logger.info(f'Removing user [{user.email}] from reviewer [{reviewer.actor_id}]')
        reviewer_map = ReviewerMapModel.query.filter_by(
            user_id=user.id,
            reviewer_id=reviewer.id
        ).first()
        if not reviewer_map:
            current_app.logger.warning(f'No mapping found for user [{user.email}] and reviewer [{reviewer.actor_id}]')
            return reviewer

        ReviewerMapModel.delete(reviewer_map)

        reviewer = self.record_cls.get(reviewer_id)
        return reviewer

    def get_members(self, identity, id):
        """Get members for a reviewer by ID."""
        self.require_permission(identity, "read")

        reviewer = self.record_cls.get(id)
        if not reviewer:
            raise Exception(f"Reviewer {id} not found")

        member_data = []
        for member in reviewer.members:
            member_data.append({
                "id": member.id,
                "email": member.email
            })

        return member_data