"""
Production settings for BIMS2 project.
"""

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']  # Configure with actual domain in production

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
