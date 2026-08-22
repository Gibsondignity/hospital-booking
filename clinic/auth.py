"""Authentication-first permission checks for internal clinic routes."""

from django.contrib.auth.decorators import login_required, permission_required


def clinic_permission_required(permission):
    def decorator(view):
        return login_required(permission_required(permission, raise_exception=True)(view))

    return decorator
