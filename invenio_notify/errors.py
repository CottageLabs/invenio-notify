class NotExistsError(Exception):
    """not found exception."""

    def __init__(self, id_):
        self.id = id_

    @property
    def description(self):
        """Exception's description."""
        return f"Record with id {self.id} is not found."


class COARProcessFail(Exception):

    def __init__(self, status, msg):
        self.status = status
        self.msg = msg
