from flask_babel import gettext as _
from sqlalchemy import asc, desc


class SortDirectionMixin:
    sort_direction_default = "asc"
    sort_direction_options = {
        "asc": dict(
            title=_("Ascending"),
            fn=asc,
        ),
        "desc": dict(
            title=_("Descending"),
            fn=desc,
        ),
    }


class DefaultSearchOptions(SortDirectionMixin):
    sort_default = "id"
    sort_options = {}
    pagination_options = {
        "default_results_per_page": 25,
    }
