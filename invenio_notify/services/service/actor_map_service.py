#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from .base_service import BasicDbService


class ActorMapService(BasicDbService):

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        if filter_maker is None:
            def filter_maker(query_param):
                filters = []
                if query_param:
                    filters.extend([
                        self.record_cls.actor_id == query_param,
                    ])
                return filters

        return super().search(identity, params, search_preference, expand, filter_maker, **kwargs)