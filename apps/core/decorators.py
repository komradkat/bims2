from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings


def role_required(allowed_roles=[]):
    """
    Decorator for views that checks whether a user has a specific role,
    redirecting to the login page if necessary.

    Usage:
    @role_required(['admin', 'treasurer'])
    def my_view(request):
        ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('core:login')}?next={request.path}")

            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            messages.error(request, "You do not have permission to access this page.")
            return redirect("core:dashboard")

        return _wrapped_view

    return decorator




def non_bootstrap_required(view_func):
    """
    Decorator for views that checks if the user is a bootstrap account.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('core:login')}?next={request.path}")

        if request.user.is_bootstrap:
            messages.error(
                request,
                "This function is disabled for bootstrapping accounts. Please create and use an official account.",
            )
            return redirect("core:dashboard")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
