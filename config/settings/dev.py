"""
Development settings for BIMS2 project.
"""

from .base import *  # noqa: F403, F405

# ALLOWED_HOSTS is now handled via .env in base.py

# Development-specific apps
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += [  # noqa: F405
        "debug_toolbar",
    ]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE  # noqa: F405
except ImportError:
    pass

INTERNAL_IPS = [
    "127.0.0.1",
]
