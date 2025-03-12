import click
from flask.cli import with_appcontext
from sqlalchemy import desc

from invenio_notify import tasks
from invenio_notify.records.models import EndorsementMetadataModel, NotifyInboxModel


@click.group(chain=True)
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
    print('Endorsement: ')
    for r in get_sorted_records(EndorsementMetadataModel, size, order_field=desc('created')):
        print('----------------------------')
        for k, v in vars(r).items():
            print_key_value(k, v)
    print()

    print('NotifyInboxModel: ')
    for r in get_sorted_records(NotifyInboxModel, size, order_field=desc('created')):
        print('----------------------------')
        for k, v in vars(r).items():
            print_key_value(k, v)
    print()


def print_key_value(k, v):
    print(f'{k:<20}: {v}')
