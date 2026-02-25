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


def tier_required(required_tiers):
    """
    Decorator to restrict view access based on license tier.

    DEBUG MODE: When DEBUG=True, bypasses tier check for development.

    Usage:
    @tier_required(['pro', 'ultra'])
    def my_view(request):
        ...

    Args:
        required_tiers: List of tier names that can access this view
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # DEBUG MODE: Bypass tier check for development
            if settings.DEBUG:
                return view_func(request, *args, **kwargs)

            # Get current tier from request (set by middleware)
            current_tier = getattr(request, "license", {}).get("tier", "community")

            if current_tier in required_tiers:
                return view_func(request, *args, **kwargs)

            # Access denied - show error message
            tier_names = "/".join([t.upper() for t in required_tiers])
            messages.error(
                request,
                f"This feature requires a {tier_names} license. "
                f"Your current tier: {current_tier.upper()}",
            )
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
