from flask_resources import route

from .basic_db_resource import BasicDbResource


class InboxAdminResource(BasicDbResource):

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            # route("POST", routes["list"], self.create),
            route("GET", routes["item"], self.read),
            route("GET", routes["list"], self.search),
            route("DELETE", routes["item"], self.delete),  # KTODO fix delete fail in inbox admin page
            # route("PUT", routes["item"], self.update),
        ]