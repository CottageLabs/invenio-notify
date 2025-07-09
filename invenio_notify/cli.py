from datetime import datetime

import click
import rich
from flask.cli import with_appcontext
from invenio_db import db
from rich.markdown import Markdown
from sqlalchemy import desc

from invenio_notify import tasks
from invenio_notify.records.models import EndorsementModel, NotifyInboxModel, ReviewerMapModel, ReviewerModel
from invenio_notify.utils import user_utils


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
    for r in get_sorted_records(EndorsementModel, size, order_field=desc('created')):
        print('----------------------------')
        key_values = vars(r).items()
        key_values = (i for i in key_values if not i[0].startswith('_'))
        for k, v in key_values:
            print_key_value(k, v)
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
        console.print_json(data=r.raw)
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
@click.argument('actor_ids', nargs=-1, required=True)
@with_appcontext
def add(email, actor_ids):
    """ assign coarnotify role and reviewer ids to user """
    from invenio_notify.proxies import current_reviewer_service

    print(f'Assigning reviewer_id(s) {actor_ids} to user[{email}]')
    user = user_utils.find_user_by_email(email)
    if user is None:
        print(f'User with email {email} not found.')
        return

    user_utils.add_coarnotify_action(db, user.id)

    assigned_count = 0
    for actor_id in actor_ids:
        if ReviewerModel.has_member_with_email(email, actor_id):
            print(f'User {user.email} already has reviewer ID ({actor_id}) assigned.')
            continue

        reviewer_id = db.session.query(ReviewerModel.id).filter_by(actor_id=actor_id).scalar()

        if reviewer_id:
            current_reviewer_service.add_member_by_emails(reviewer_id, [email])
            assigned_count += 1
        else:
            print(f"No reviewer found with actor ID: {actor_id}")

    if assigned_count:
        db.session.commit()
        print(f'Successfully assigned {assigned_count} new reviewer ID(s) to {email}')


@notify.command()
@click.option('--email', '-e', type=str, help='Email of user to assign the reviewer to')
@with_appcontext
def test_data(email):
    """Generate test data for ReviewerModel."""
    from invenio_notify.proxies import current_reviewer_service

    print("Generating a test record for ReviewerModel...")
    
    # Generate reviewer record
    reviewer = ReviewerModel.create({
        'name': "Peer Community in Evolutionary Biology",
        'actor_id': 'https://evolbiol.peercommunityin.org/coar_notify/',
        'inbox_url': "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
        'description': f"Test reviewer generated on {datetime.now().strftime('%Y-%m-%d')}"
    })
    
    print(f"Created reviewer: {reviewer.name} with actor ID: {reviewer.actor_id}")

    # If email is provided, create a ReviewerMapModel for the user
    if email:
        user = user_utils.find_user_by_email(email)
        if user is None:
            print(f"User with email {email} not found. Reviewer created but not assigned to any user.")
        else:
            # Add required role to the user
            user_utils.add_coarnotify_action(db, user.id)
            
            # Add the user as a member
            current_reviewer_service.add_member_by_email(reviewer.id, email)
            print(f"Created reviewer mapping: {email} -> {reviewer.name}")

    db.session.commit()
    print("Successfully created test reviewer record")


@notify.group()
def dummy_pci():
    """Dummy PCI commands for testing"""


@dummy_pci.command()
def list():
    """List all received notifications in dummy PCI store"""
    from invenio_notify.dummy_reviewer.dummy_pci_app import DummyPCIBackend
    
    backend = DummyPCIBackend()
    backend.print_notifications()


@dummy_pci.command()
@click.option('--type', '-t', default='endorsement_resp', 
              type=click.Choice(['endorsement_resp', 'review', 'tentative_accept', 'reject']),
              help='Type of reply payload to send')
def reply(type):
    """Reply to the last notification in store"""
    from invenio_notify.dummy_reviewer.dummy_pci_app import DummyPCIBackend
    
    backend = DummyPCIBackend()
    backend.reply_last(type)


@dummy_pci.command()
def run():
    """Run the dummy PCI server"""
    from invenio_notify.dummy_reviewer.dummy_pci_app import run
    
    run()

