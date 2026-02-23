"""
Production settings for BIMS2 project.
"""

from .base import *

# DEBUG and ALLOWED_HOSTS are now handled via .env in base.py

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
