from flask_resources import route

from .basic_db_resource import BasicDbResource


class EndorsementAdminResource(BasicDbResource):

    def create_url_rules(self):
        """Create the URL rules for the endorsement admin resource."""
        routes = self.config.routes
        return [
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
        ]