import click
import json
import rich
from flask.cli import with_appcontext
from invenio_accounts.models import User
from invenio_db import db
from rich.markdown import Markdown
from sqlalchemy import desc

from invenio_notify import tasks
from invenio_notify.records.models import EndorsementMetadataModel, NotifyInboxModel, ReviewerMapModel


def print_key_value(k, v):
    print(f'{k:<20}: {v}')


@click.group(chain=False)
def notify():
    """Notify commands."""


@notify.command()
@with_appcontext
def run():
    """Run the notify background job"""
    tasks.inbox_processing()


def get_sorted_records(model_class, size=None, order_field=None):
    """Get records sorted by created date in descending order with optional limit."""
    query = model_class.query
    if order_field is not None:
        query = query.order_by(order_field)

    if size:
        query = query.limit(size)
    return query.all()


@notify.command()
@click.option('--size', '-s', type=int, default=1000, help='Maximum number of records to display')
@with_appcontext
def list_notify(size):
    """ List latest endorsement and notify inbox records """

    console = rich.get_console()
    console.print(Markdown('# Endorsement'))
    for r in get_sorted_records(EndorsementMetadataModel, size, order_field=desc('created')):
        print('----------------------------')
        key_values = vars(r).items()
        key_values = (i for i in key_values if i[0] != 'json')
        key_values = (i for i in key_values if not i[0].startswith('_'))
        for k, v in key_values:
            print_key_value(k, v)
        console.print('Json:')
        console.print_json(json.dumps(r.json))
        print()
    print()

    console.print(Markdown('# Notify Inbox'))
    for r in get_sorted_records(NotifyInboxModel, size, order_field=desc('created')):
        print('----------------------------')
        key_values = vars(r).items()
        key_values = (i for i in key_values if i[0] != 'raw')
        key_values = (i for i in key_values if not i[0].startswith('_'))
        for k, v in key_values:
            print_key_value(k, v)
        console.print('Raw:')
        console.print_json(r.raw)
        print()


@notify.group()
def user():
    """User commands"""


@user.command()
@click.option('-u', '--user', type=str, help='query by user email')
@click.option('-r', '--reviewer_id', type=str, help='query by reviewer id')
@with_appcontext
def list(user, reviewer_id):
    """ List user and reviewer id mapping """
    if user:
        rows = ReviewerMapModel.find_by_email(user)
    elif reviewer_id:
        rows = ReviewerMapModel.find_by_reviewer_id(reviewer_id)
    else:
        print('Please provide either email or reviewer_id to query.')
        return

    print('List of users and reviewer ids:')
    for r in rows:
        print(f'{r.user.email:<40} -> [{r.reviewer_id}]')


@user.command()
@click.argument('email')
@click.argument('reviewer_id')
@with_appcontext
def add(email, reviewer_id):
    """ assign coarnotify role and reviewer id to user """
    from invenio_notify.utils import user_utils

    print(f'Assign reviewer_id[{reviewer_id}] to user[{email}]')
    user = User.query.filter_by(email=email).first()
    if user is None:
        print(f'User with email {email} not found.')
        return

    user_utils.add_user_action(db, user.id)

    if ReviewerMapModel.query.filter_by(user_id=user.id, reviewer_id=reviewer_id).scalar():
        print(f'User {user.email} already has a reviewer ID ({reviewer_id}) assigned.')
        return

    ReviewerMapModel.create({
        'user_id': user.id,
        'reviewer_id': reviewer_id,
    })
    db.session.commit()

