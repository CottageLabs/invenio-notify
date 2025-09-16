import os.path
from datetime import datetime, timezone

import click
import rich
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_db import db
from rich.markdown import Markdown
from sqlalchemy import desc

from invenio_notify import tasks
from invenio_notify.records.models import EndorsementModel, NotifyInboxModel, ActorMapModel, ActorModel
from invenio_notify.utils import user_utils


def print_key_value(k, v):
    print(f'{k:<20}: {v}')


def get_sorted_records(model_class, size=None, order_field=None):
    """Get records sorted by created date in descending order with optional limit."""
    query = model_class.query
    if order_field is not None:
        query = query.order_by(order_field)

    if size:
        query = query.limit(size)
    return query.all()


@click.group(chain=False)
def notify():
    """Notify commands."""


# =============================================================================
# Main notify commands
# =============================================================================

@notify.command()
@with_appcontext
def run():
    """Run the notify background job"""
    tasks.inbox_processing()


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


@notify.command()
@click.option('--email', '-e', type=str, help='Email of user to assign the actor to')
@with_appcontext
def test_data(email):
    """Generate test data for ActorModel."""
    from invenio_notify.proxies import current_actor_service

    print("Generating a test record for ActorModel...")

    # Generate actor record
    actor = ActorModel.create({
        'name': "Peer Community in Evolutionary Biology",
        'actor_id': 'https://evolbiol.peercommunityin.org/coar_notify/',
        'inbox_url': "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
        'description': f"Test actor generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    })

    print(f"Created actor: {actor.name} with actor ID: {actor.actor_id}")

    # If email is provided, create a ActorMapModel for the user
    if email:
        user = user_utils.find_user_by_email(email)
        if user is None:
            print(f"User with email {email} not found. Actor created but not assigned to any user.")
        else:
            # Add required role to the user
            user_utils.add_coarnotify_action(db, user.id)

            # Add the user as a member using system identity (bypasses permissions for CLI)
            current_actor_service.add_member(system_identity, actor.id, {'emails': [email]})
            print(f"Created actor mapping: {email} -> {actor.name}")

    db.session.commit()
    print("Successfully created test actor record")


# =============================================================================
# User management commands
# =============================================================================

@notify.group()
def user():
    """User commands"""


@user.command()
@click.option('-u', '--user', type=str, help='query by user email')
@click.option('-r', '--actor_id', type=str, help='query by actor id')
@with_appcontext
def list(user, actor_id):
    """ List user and actor id mapping """
    if user:
        rows = ActorMapModel.find_by_email(user)
    elif actor_id:
        rows = ActorMapModel.find_by_actor_id(actor_id)
    else:
        print('Please provide either email or actor_id to query.')
        return

    print('List of users and actor ids:')
    for r in rows:
        print(f'{r.user.email:<40} -> [{r.actor_id}]')


@user.command()
@click.argument('email')
@click.argument('actor_ids', nargs=-1, required=True)
@with_appcontext
def add(email, actor_ids):
    """ assign coarnotify role and actor ids to user """
    from invenio_notify.proxies import current_actor_service

    print(f'Assigning actor_id(s) {actor_ids} to user[{email}]')
    user = user_utils.find_user_by_email(email)
    if user is None:
        print(f'User with email {email} not found.')
        return

    user_utils.add_coarnotify_action(db, user.id)

    assigned_count = 0
    for actor_id in actor_ids:
        if ActorModel.has_member_with_email(email, actor_id):
            print(f'User {user.email} already has actor ID ({actor_id}) assigned.')
            continue

        actor_id = db.session.query(ActorModel.id).filter_by(actor_id=actor_id).scalar()

        if actor_id:
            # Use system identity to bypass permissions for CLI operations
            current_actor_service.add_member(system_identity, actor_id, {'emails': [email]})
            assigned_count += 1
        else:
            print(f"No actor found with actor ID: {actor_id}")

    if assigned_count:
        db.session.commit()
        print(f'Successfully assigned {assigned_count} new actor ID(s) to {email}')


# =============================================================================
# Dummy PCI testing commands
# =============================================================================

@notify.group()
def dummy_pci():
    """Dummy PCI commands for testing"""


@dummy_pci.command()
def list():
    """List all received notifications in dummy PCI store"""
    from invenio_notify.dummy_actor.dummy_pci_app import DummyPCIBackend
    
    backend = DummyPCIBackend()
    backend.print_notifications()


@dummy_pci.command()
@click.option('--type', '-t', default='endorsement', 
              type=click.Choice(['endorsement', 'review', 'tentative_accept',
                                 'tentative_reject', 'reject']),
              help='Type of reply payload to send')
@click.option('--token', help='token that used to notify api' )
def reply(token, type):
    """Reply to the last notification in store"""
    from invenio_notify.dummy_actor.dummy_pci_app import DummyPCIBackend
    
    backend = DummyPCIBackend()
    backend.reply_last(token, payload_type=type)


@dummy_pci.command()
def run():
    """Run the dummy PCI server"""
    from invenio_notify.dummy_actor import dummy_pci_app
    p = os.path.abspath(dummy_pci_app.__file__)
    print('****************************************')
    print("You have to run the following command manually:")
    print(f'python {p}')
    print('****************************************')


@dummy_pci.command()
def reset():
    """Reset dummy PCI store to empty list"""
    from invenio_notify.dummy_actor.dummy_pci_app import DummyPCIBackend
    
    backend = DummyPCIBackend()
    backend.reset()
    print("Dummy PCI store reset to empty list")

