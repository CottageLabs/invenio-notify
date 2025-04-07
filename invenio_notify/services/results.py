from invenio_records_resources.services.records.results import RecordList

try:
    # flask_sqlalchemy<3.0.0
    from flask_sqlalchemy import Pagination
except ImportError:
    # flask_sqlalchemy>=3.0.0
    from flask_sqlalchemy.pagination import Pagination


class BasicDbModelRecordList(RecordList):
    """ support db model result to record list"""

    def __init__(
            self,
            service,
            identity,
            results,
            params=None,
            links_tpl=None,
            links_item_tpl=None,
            schema=None,
    ):
        """Constructor."""
        super().__init__(
            service, identity, results, params, links_tpl, links_item_tpl, schema
        )

    @property
    def hits(self):
        """Iterator over the hits."""
        for record in self.results():
            # yield record

            # Project the record
            projection = self._schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                ),
            )

            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, record
                )

            yield projection

    def to_dict(self):
        res = {
            "hits": {
                "hits": list(self.hits),
                "total": self.total,
            }
        }

        if self._params:
            if self._links_tpl:
                res["links"] = self._links_tpl.expand(self._identity, self.pagination)

        return res

    @property
    def total(self):
        return (
            self._results.total
            if isinstance(self._results, Pagination)
            else len(self._results)
        )

    def results(self):
        return (
            self._results.items
            if isinstance(self._results, Pagination)
            else self._results
        )
