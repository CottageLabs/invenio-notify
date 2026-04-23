#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from functools import wraps

from flask import Blueprint

from .constants import NOTIFY_ENDORSEMENT_RECEIVE, NOTIFY_ENDORSEMENT_REQUEST


def is_pci_endorsement_enabled(app=None):
    if app is None:
        from flask import current_app
        app = current_app
    return app.config.get(NOTIFY_ENDORSEMENT_RECEIVE, False)


def is_pci_announcement_of_endorsement_enabled(app=None):
    if app is None:
        from flask import current_app
        app = current_app
    return is_pci_endorsement_enabled(app) and app.config.get(NOTIFY_ENDORSEMENT_REQUEST, False)


class NotifyFeatureBlueprintEnable:
    """Class-based decorator to enable/disable blueprint registration based on feature settings."""

    def __init__(self, feature_check_func):
        """Initialize with the feature checking function."""
        self.feature_check_func = feature_check_func

    def __call__(self, func):
        """Make the class callable as a decorator."""

        @wraps(func)
        def wrapper(app):
            if not self.feature_check_func(app=app):
                return Blueprint(f'empty_blueprint_{func.__name__}', __name__)
            return func(app)

        return wrapper


# Create instances for each feature
pci_endorsement_blueprint_enable = NotifyFeatureBlueprintEnable(is_pci_endorsement_enabled)
pci_announcement_of_endorsement_enable = NotifyFeatureBlueprintEnable(is_pci_announcement_of_endorsement_enabled)


class PCIEndorsementAdminDisabledMixin:
    """Mixin class for admin views to determine if they should be disabled."""

    @staticmethod
    def disabled():
        """Determine if the view should be disabled."""
        return not is_pci_endorsement_enabled()


class PCIAnnouncementOfEndorsementAdminDisabledMixin:
    """Mixin class for admin views to determine if they should be disabled."""

    @staticmethod
    def disabled():
        """Determine if the view should be disabled."""
        return not is_pci_announcement_of_endorsement_enabled()
