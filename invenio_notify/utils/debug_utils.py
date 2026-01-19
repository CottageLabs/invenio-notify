#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

import traceback

import sys


def print_exception_stack():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback)


def print_all_app_config(app):
    print('All app.config items:')
    for k, v in app.config.items():
        try:
            print(f"{k} = {v}")
        except Exception as e:
            pass
