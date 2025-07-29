from .base_service import BasicDbService


class ReviewerMapService(BasicDbService):

    def search(self, identity, params=None, search_preference=None, expand=False, filter_maker=None, **kwargs):
        if filter_maker is None:
            def filter_maker(query_param):
                filters = []
                if query_param:
                    filters.extend([
                        self.record_cls.reviewer_id == query_param,
                    ])
                return filters

        return super().search(identity, params, search_preference, expand, filter_maker, **kwargs)