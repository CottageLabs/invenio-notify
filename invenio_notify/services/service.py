import regex
from flask import current_app
from flask import g
from invenio_accounts.models import User
from invenio_db import db
from invenio_db.uow import unit_of_work
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.base.utils import map_search_params
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from sqlalchemy.orm import with_loader_criteria, selectinload

from coarnotify.core.notify import NotifyPattern
from coarnotify.server import COARNotifyServiceBinding, COARNotifyReceipt, COARNotifyServer
from invenio_notify import constants
from invenio_notify.errors import COARProcessFail
from invenio_notify.proxies import current_inbox_service
from invenio_notify.records.models import ReviewerMapModel, ReviewerModel, EndorsementModel
from invenio_notify.utils import user_utils
from invenio_notify.utils.notify_utils import get_recid_by_record_url
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services import RDMRecordService

re_url_record_id = regex.compile(r'/records/(.*?)$')


class BasicDbService(RecordService):

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        self.require_permission(identity, "search")

        params = params or {}

        search_params = map_search_params(self.config.search, params)
        query_param = search_params["q"]

        filters = []
        if filter_maker:
            filters.extend(filter_maker(query_param))

        record_list = self.record_cls.search(search_params, filters)
        record_list = list(record_list)

        return self.result_list(
            self,
            identity,
            record_list,
            params=search_params,
            links_tpl=LinksTemplate(self.config.links_search, context={"args": params}),
            links_item_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def delete(self, identity, id, uow=None):
        self.require_permission(identity, "delete")

        record = self.record_cls.get(id)
        self.record_cls.delete(record)

        return self.result_item(self, identity, record, links_tpl=self.links_item_tpl)

    def read(self, identity, id):
        self.require_permission(identity, "read")

        record = self.record_cls.get(id)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def create(self, identity, data, raise_errors=True, uow=None, schema=None):
        self.require_permission(identity, "create")

        schema = schema or self.schema

        # validate data
        valid_data, errors = schema.load(
            data,
            context={"identity": identity},
            raise_errors=raise_errors,
        )

        record = self.record_cls.create(valid_data)

        return self.result_item(
            self, identity, record, links_tpl=self.links_item_tpl, errors=errors
        )

    @unit_of_work()
    def update(self, identity, id, data, uow=None):
        self.require_permission(identity, "update")

        record = self.record_cls.get(id)

        # validate data
        valid_data, errors = self.schema.load(
            data,
            context={"identity": identity},
            raise_errors=True,
        )

        self.record_cls.update(valid_data, id)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )


class NotifyInboxService(BasicDbService):

    def receive_notification(self, notification_raw: dict) -> COARNotifyReceipt:
        server = COARNotifyServer(InboxCOARBinding())
        current_app.logger.debug(f'input announcement:')
        result = server.receive(notification_raw, validate=True)
        current_app.logger.debug(f'result: {result}')
        return result

    @property
    def schema_api(self):
        return ServiceSchemaWrapper(self, schema=self.config.schema_api)

    @unit_of_work()
    def create(self, identity, data, raise_errors=True, uow=None):
        data['user_id'] = identity.id
        return super().create(
            identity,
            data,
            raise_errors=raise_errors,
            uow=uow,
            schema=self.schema_api
        )


class InboxCOARBinding(COARNotifyServiceBinding):

    def notification_received(self, notification: NotifyPattern) -> COARNotifyReceipt:
        current_app.logger.debug('called notification_received')

        raw = notification.to_jsonld()
        recid = get_recid_by_record_url(raw['context']['id'])

        # Check actor_id match with user
        actor_id = raw['actor']['id']
        if not ReviewerModel.has_member(g.identity.id, actor_id):
            current_app.logger.warning(f'Actor id not match with user: {actor_id}, {g.identity.id}')
            raise COARProcessFail(constants.STATUS_FORBIDDEN, 'Actor Id mismatch')

        # Check if the notification type is supported
        if all(t not in constants.REVIEW_TYPES for t in raw.get('type', [])):
            current_app.logger.info(f'Unknown type: [{recid=}]{raw.get("type")}')
            raise COARProcessFail(constants.STATUS_NOT_ACCEPTED, 'Notification type not supported')

        # check if record exists
        records_service: RDMRecordService = current_rdm_records_service
        records_service.record_cls.pid.resolve(recid)  # raises PIDDoesNotExistError if not found

        current_app.logger.debug(f'client input raw: {raw}')
        current_inbox_service.create(g.identity, {"raw": raw, 'recid': recid})

        return COARNotifyReceipt(COARNotifyReceipt.ACCEPTED)


class EndorsementService(BasicDbService):
    """Service for managing endorsements."""

    def get_endorsement_info(self, record_id):
        """Get the endorsement information for a record by its ID.
        
        Args:
            record_id: The UUID of the record
            
        Returns:
            list: A list of dictionaries containing endorsement information
        """
        if not record_id:
            return []

        # Find all reviewers who have endorsed this record using EXISTS
        reviewers = (
            db.session.query(ReviewerModel)
            .filter(
                db.exists().where(
                    db.and_(
                        EndorsementModel.reviewer_id == ReviewerModel.id,
                        EndorsementModel.record_id == record_id
                    )
                )
            )
            .options(
                selectinload(ReviewerModel.endorsements),
                with_loader_criteria(EndorsementModel, lambda e: e.record_id == record_id)
            ).all()
        )

        if not reviewers:
            return []

        result = []
        for reviewer in reviewers:
            endorsements = reviewer.endorsements
            endorsement_count = sum(1 for e in endorsements if e.review_type == constants.TYPE_ENDORSEMENT)
            review_count = sum(1 for e in endorsements if e.review_type == constants.TYPE_REVIEW)

            sub_endorsement_list = []
            for e in endorsements:
                if e.review_type == constants.TYPE_ENDORSEMENT:
                    sub_endorsement_list.append({
                        'created': e.created.isoformat(),
                        'url': e.result_url
                    })

            result.append({
                'reviewer_id': reviewer.id,
                'reviewer_name': reviewer.name,
                'endorsement_count': endorsement_count,
                'review_count': review_count,
                'endorsement_list': sub_endorsement_list,
            })

        return result


class ReviewerMapService(BasicDbService):

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        if filter_maker is None:
            def filter_maker(query_param):
                filters = []
                if query_param:
                    filters.extend([
                        self.record_cls.reviewer_id == query_param,
                    ])
                return filters

        return super().search(identity, params, search_preference, expand, filter_maker, **kwargs)


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

        # validate data
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

        added_members = []
        for email in new_emails:
            user = user_utils.find_user_by_email(email)
            if user:
                current_app.logger.info(f'Adding user [{user.email}] to reviewer [{reviewer.coar_id}]')
                ReviewerMapModel.create({
                    'user_id': user.id,
                    'reviewer_id': reviewer.id
                })
                user_utils.add_coarnotify_action(db, user.id)
                added_members.append(user)
            else:
                current_app.logger.warning(f'User with email {email} not found')

        reviewer = self.record_cls.get(reviewer_id)
        return reviewer

    def del_member(self, identity, id, data, raise_errors=True):
        self.require_permission(identity, "update")

        # validate data
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
            current_app.logger.info(f'User [{user.email}] is not a member of reviewer [{reviewer.coar_id}]')
            return reviewer

        current_app.logger.info(f'Removing user [{user.email}] from reviewer [{reviewer.coar_id}]')
        reviewer_map = ReviewerMapModel.query.filter_by(
            user_id=user.id,
            reviewer_id=reviewer.id
        ).first()
        if not reviewer_map:
            current_app.logger.warning(f'No mapping found for user [{user.email}] and reviewer [{reviewer.coar_id}]')
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

        # Transform members data for API consumption
        member_data = []
        for member in reviewer.members:
            member_data.append({
                "id": member.id,
                "email": member.email
            })

        return member_data
