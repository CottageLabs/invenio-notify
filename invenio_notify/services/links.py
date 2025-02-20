from invenio_records_resources.services import Link


class EndorsementLink(Link):

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update(
            {
                "id": record.id,
            }
        )
