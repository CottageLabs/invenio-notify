from functools import wraps

from flask import Blueprint

from .constants import CONFIG_NOTIFY_PHASE_1_ENABLED, CONFIG_NOTIFY_PHASE_2_ENABLED


def is_phase_1_enabled(app=None):
    from flask import current_app
    target_app = app or current_app
    return target_app.config.get(CONFIG_NOTIFY_PHASE_1_ENABLED, False)


def is_phase_2_enabled(app=None):
    from flask import current_app
    target_app = app or current_app
    return is_phase_1_enabled(app) and target_app.config.get(CONFIG_NOTIFY_PHASE_2_ENABLED, False)


class PhaseBlueprintEnable:
    """Class-based decorator to enable/disable blueprint registration based on phase settings."""

    def __init__(self, phase_check_func):
        """Initialize with the phase checking function."""
        self.phase_check_func = phase_check_func

    def __call__(self, func):
        """Make the class callable as a decorator."""

        @wraps(func)
        def wrapper(app):
            if not self.phase_check_func(app=app):
                return Blueprint(f'empty_blueprint_{func.__name__}', __name__)
            return func(app)

        return wrapper


# Create instances for each phase
phase_1_blueprint_enable = PhaseBlueprintEnable(is_phase_1_enabled)
phase_2_blueprint_enable = PhaseBlueprintEnable(is_phase_2_enabled)


class Phase1AdminDisabledMixin:
    """Mixin class for admin views to determine if they should be disabled."""

    @staticmethod
    def disabled():
        """Determine if the view should be disabled."""
        return not is_phase_1_enabled()


class Phase2AdminDisabledMixin:
    """Mixin class for admin views to determine if they should be disabled."""

    @staticmethod
    def disabled():
        """Determine if the view should be disabled."""
        return not is_phase_2_enabled()
