"""
License verification middleware for BIMS2.
Checks and caches active license on each request.

DEBUG MODE: When DEBUG=True, automatically grants Ultra tier for development.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from apps.core.models import LicenseKey
from apps.core.utils.hardware import get_hardware_id


class LicenseVerificationMiddleware:
    """
    Middleware to verify license on each request.
    
    - Checks for active license bound to this server's hardware ID
    - Caches license data for 1 hour to minimize database queries
    - Defaults to Community tier if no license found
    - Attaches license data to request object
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require license verification
        self.exempt_paths = ['/login/', '/logout/', '/license/activate/', '/admin/', '/static/']
    
    def __call__(self, request):
        # DEBUG MODE: Bypass license check and grant Ultra tier for development
        if settings.DEBUG:
            request.license = {
                'tier': 'ultra',
                'max_users': 999,
                'expiry_date': None,
                'key_preview': 'DEBUG MODE (Ultra)'
            }
            return self.get_response(request)
        
        # Skip license check for exempt paths
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)
        
        # Check cached license
        license_data = cache.get('active_license')
        
        if not license_data:
            # Fetch from database
            hardware_id = get_hardware_id()
            try:
                license_key = LicenseKey.objects.get(
                    hardware_id=hardware_id,
                    is_active=True
                )
                if license_key.is_valid():
                    license_data = {
                        'tier': license_key.tier,
                        'max_users': license_key.max_users,
                        'expiry_date': str(license_key.expiry_date) if license_key.expiry_date else None,
                        'key_preview': license_key.key[:8] + '...' if len(license_key.key) > 8 else license_key.key
                    }
                    # Cache for 1 hour
                    cache.set('active_license', license_data, 3600)
                else:
                    # License exists but is invalid (expired or inactive)
                    # Redirect to activation page for renewal
                    if not request.path.startswith('/license/'):
                        return redirect(reverse('core:license_activation'))
            except LicenseKey.DoesNotExist:
                # No license found - default to Community tier
                license_data = {
                    'tier': 'community',
                    'max_users': 5,
                    'expiry_date': None,
                    'key_preview': 'Community (Free)'
                }
                # Cache for 1 hour
                cache.set('active_license', license_data, 3600)
        
        # Attach license to request
        request.license = license_data
        
        response = self.get_response(request)
        return response
