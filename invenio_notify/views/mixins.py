from flask import current_app


class NotifyAdminDisabledMixin:
    """Mixin class for admin views to determine if they should be disabled."""

    @staticmethod
    def disabled():
        """Determine if the view should be disabled."""
        return not current_app.config.get("NOTIFY_FEATURE_ENABLED", True)
