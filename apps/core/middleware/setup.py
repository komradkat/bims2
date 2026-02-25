from django.shortcuts import redirect
from django.urls import reverse
from apps.core.models import BarangayInfo


class SetupRequiredMiddleware:
    """
    Middleware that checks if the system has been set up (BarangayInfo exists).
    If not, redirects all requests to the setup page, except for:
    - The setup page itself
    - Static/Media files
    - Admin (maybe? better to force setup first)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths exempt from setup check
        exempt_paths = [
            reverse("core:setup"),
            "/static/",
            "/media/",
            "/favicon.ico",
        ]

        # If current path implies we are already going to setup or fetching assets
        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # Check if Barangay Info exists
        has_info = BarangayInfo.objects.exists()

        if not has_info:
            return redirect("core:setup")

        response = self.get_response(request)
        return response
