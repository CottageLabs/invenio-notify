"""Errors."""

import marshmallow as ma
import sqlalchemy.orm.exc
from flask_resources import HTTPJSONException, create_error_handler
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.errors import validation_error_to_list_errors

from invenio_notify.errors import NotExistsError, SendRequestFail, BadRequestError


def create_description(e, description_fn=None):
    """Generate description from exception."""
    if description_fn:
        return description_fn(e)
    if hasattr(e, 'description'):
        return e.description
    return str(e)


def create_error_handler_with_json(code, description_fn=None):
    return create_error_handler(
        lambda e: HTTPJSONException(
            code=code,
            description=create_description(e, description_fn=description_fn),
        )
    )

class HTTPJSONValidationException(HTTPJSONException):
    """HTTP exception serializing to JSON and reflecting Marshmallow errors."""

    description = "A validation error occurred."

    def __init__(self, exception):
        """Constructor."""
        super().__init__(code=400, errors=validation_error_to_list_errors(exception))


class ErrorHandlersMixin:
    """Mixin to define error handlers."""

    error_handlers = {
        NotExistsError: create_error_handler_with_json(404),
        ma.ValidationError: create_error_handler(
            lambda e: HTTPJSONValidationException(e)
        ),
        ValueError: create_error_handler_with_json(400),
    }



class ApiErrorHandlersMixin(ErrorHandlersMixin):
    """API error handlers mixin."""

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        SendRequestFail: create_error_handler_with_json(400),
        PIDDoesNotExistError: create_error_handler_with_json(404),
        sqlalchemy.orm.exc.NoResultFound: create_error_handler_with_json(404, 'Data not found.'),
        BadRequestError: create_error_handler_with_json(400),
    }
