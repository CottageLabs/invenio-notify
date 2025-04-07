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
