#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from invenio_records_resources.services import Link


class IdLink(Link):

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update(
            {
                "id": record.id,
            }
        )


class EndorsementLink(IdLink):
    pass


class NotifyInboxLink(IdLink):
    pass
