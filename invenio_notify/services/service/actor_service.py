from flask import current_app
from invenio_accounts.models import User
from invenio_db.uow import unit_of_work
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper

from invenio_notify.records.models import ActorMapModel, ActorModel
from invenio_notify.utils import user_utils, actor_utils
from .base_service import BasicDbService


class ActorService(BasicDbService):
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

    @unit_of_work()
    def add_member(self, identity, id, data, raise_errors=True, uow=None):
        self.require_permission(identity, "update")

        valid_data, errors = self.schema_add_member.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        # Inline the functionality from add_member_by_emails with proper permission check
        actor: ActorModel = self.record_cls.get(id)
        emails = valid_data['emails']

        new_emails = set(emails)
        existing_emails = {m.email for m in actor.members}
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
                current_app.logger.info(f'Adding user [{user.email}] to actor [{actor.actor_id}]')
                actor_utils.add_member_to_actor(id, user.id, uow=uow)
            else:
                current_app.logger.warning(f'User with email {email} not found')

        actor = self.record_cls.get(id)
        return actor


    @unit_of_work()
    def del_member(self, identity, id, data, raise_errors=True, uow=None):
        self.require_permission(identity, "update")

        valid_data, errors = self.schema_del_member.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        # Inline the functionality from del_member_by_id with proper permission check
        actor: ActorModel = self.record_cls.get(id)
        user_id = valid_data['user_id']
        user: User = User.query.get(user_id)

        if user not in actor.members:
            current_app.logger.info(f'User [{user.email}] is not a member of actor [{actor.actor_id}]')
            return actor

        current_app.logger.info(f'Removing user [{user.email}] from actor [{actor.actor_id}]')
        actor_map = ActorMapModel.query.filter_by(
            user_id=user.id,
            actor_id=actor.id
        ).first()
        if not actor_map:
            current_app.logger.warning(f'No mapping found for user [{user.email}] and actor [{actor.actor_id}]')
            return actor

        ActorMapModel.delete(actor_map)

        actor = self.record_cls.get(id)
        return actor


    def get_members(self, identity, id):
        """Get members for a actor by ID."""
        self.require_permission(identity, "read")

        actor = self.record_cls.get(id)
        if not actor:
            raise Exception(f"Actor {id} not found")

        member_data = []
        for member in actor.members:
            member_data.append({
                "id": member.id,
                "email": member.email
            })

        return member_data