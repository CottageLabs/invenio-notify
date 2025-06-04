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
