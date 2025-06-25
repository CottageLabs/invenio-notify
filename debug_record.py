#!/usr/bin/env python
import pytest
from invenio_notify_test.conftest import *

def test_debug_record(rdm_record):
    """Debug test to see record structure."""
    print(f"Record type: {type(rdm_record)}")
    print(f"Record dir: {[x for x in dir(rdm_record) if not x.startswith('_')]}")
    if hasattr(rdm_record, 'data'):
        print(f"Record data: {rdm_record.data}")
    if hasattr(rdm_record, 'id'):
        print(f"Record id: {rdm_record.id}")
    print("Record attributes:")
    for attr in ['data', 'id', '_record']:
        if hasattr(rdm_record, attr):
            val = getattr(rdm_record, attr)
            print(f"  {attr}: {val} (type: {type(val)})")