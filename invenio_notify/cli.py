import click
import json
import rich
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
    console = rich.get_console()
    console.print('** Endorsement: **', style='bold')
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

    console.print('** Notify Inbox: **', style='bold')
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


def print_key_value(k, v):
    print(f'{k:<20}: {v}')
