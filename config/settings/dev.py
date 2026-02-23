"""
Development settings for BIMS2 project.
"""

from .base import *

# ALLOWED_HOSTS is now handled via .env in base.py

# Development-specific apps
INSTALLED_APPS += [
    # 'debug_toolbar',  # Uncomment when needed
]

# Development-specific middleware
# MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1',
]
