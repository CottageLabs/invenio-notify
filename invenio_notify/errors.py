class NotExistsError(Exception):
    """not found exception."""

    def __init__(self, id_):
        """Constructor."""
        self.id = id_

    @property
    def description(self):
        """Exception's description."""
        return f"Record with id {self.id} is not found."
