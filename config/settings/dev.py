"""
Development settings for BIMS2 project.
"""

from .base import *  # noqa: F403, F405

# ALLOWED_HOSTS is now handled via .env in base.py

# Development-specific apps
try:
    import debug_toolbar
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
except ImportError:
    pass

INTERNAL_IPS = [
    '127.0.0.1',
]
