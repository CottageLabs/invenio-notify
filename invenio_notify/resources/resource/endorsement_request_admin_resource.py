#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from flask_resources import route

from .notify_resource import NotifyResource


class EndorsementRequestAdminResource(NotifyResource):

    def create_url_rules(self):
        """Create the URL rules for the endorsement request admin resource."""
        routes = self.config.routes
        return [
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
        ]