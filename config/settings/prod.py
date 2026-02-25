"""
Production settings for BIMS2 project.
"""

from .base import *  # noqa: F403, F405
from .base import env

# DEBUG and ALLOWED_HOSTS are now handled via .env in base.py

# Additional Production Security (Overrides)
# Redundant settings (SSL_REDIRECT, HSTS, etc.) are already handled by base.py

# Proxy settings (useful if behind Nginx/Apache)
# This allows Django to trust the X-Forwarded-Proto header for HTTPS detection
SECURE_PROXY_SSL_HEADER = env.tuple(
    "SECURE_PROXY_SSL_HEADER", default=("HTTP_X_FORWARDED_PROTO", "https")
)

# For production, we can explicitly lock down specific settings if needed
# but currently we rely on the intelligent defaults in base.py
