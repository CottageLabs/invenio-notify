#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

class NotExistsError(Exception):
    """not found exception."""

    def __init__(self, id_):
        self.id = id_

    @property
    def description(self):
        """Exception's description."""
        return f"Record with id {self.id} is not found."


class COARProcessFail(Exception):

    def __init__(self, status, description):
        self.status = status
        self.description = description


class SendRequestFail(Exception):
    """Send request fail exception."""

    def __init__(self, description, status=None):
        self.status = status
        self.description = description


class BadRequestError(Exception):
    """ General error if you can 400 from error handler. """

    def __init__(self, description):
        self.description = description
