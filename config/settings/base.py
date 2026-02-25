"""
Base settings for BIMS2 project.
"""

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Filter environ to handle Profile-based overrides
class SmartProfileEnv(environ.Env):
    def __init__(self, **scheme):
        super().__init__(**scheme)
        self.profile = os.environ.get("BIMS_PROFILE", "development").lower()

    def __call__(self, var, cast=None, default=environ.Env.NOTSET, parse_default=False):
        # If in production, check for PROD_ prefix first
        if self.profile == "production":
            prod_var = f"PROD_{var}"
            if prod_var in os.environ:
                # Inherit the cast from the base variable's scheme if not explicitly provided
                if cast is None and var in self.scheme:
                    cast = self.scheme[var][0]
                return super().__call__(
                    prod_var, cast=cast, default=default, parse_default=parse_default
                )
        return super().__call__(
            var, cast=cast, default=default, parse_default=parse_default
        )


# Initialize smart environment
env = SmartProfileEnv(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Read .env file if it exists (for Development)
# We now always use .env as the source of truth, with profile overrides inside
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    environ.Env.read_env(str(ENV_FILE))

# --- Embedded Secrets (Production Hardening) ---
# For compiled distributions, we embed secrets directly in the binary.
# The build script generates config/env_secure.py which is then obfuscated.
try:
    from config import env_secure

    # Iterate over all uppercase variables in the secure module
    for key, value in env_secure.__dict__.items():
        if key.isupper():
            # Inject into the environment so environ.Env picks them up as overrides
            # Convert to string for environment, but ensure bools are handled correctly by env.bool calls later
            os.environ[key] = str(value)
except ImportError:
    # Not in a hardened environment, standard .env loading continues
    pass

# System Versioning
VERSION_FILE = BASE_DIR / "VERSION"
if VERSION_FILE.exists():
    with open(VERSION_FILE, "r") as f:
        BIMS_VERSION = f.read().strip()
else:
    BIMS_VERSION = "1.0.0-alpha"


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="django-insecure-fallback-key-change-me")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

# Safety Check: Warn if using fallback key in production-like environments
if not DEBUG and SECRET_KEY == "django-insecure-fallback-key-change-me":
    print(
        "\n[WARNING] CRITICAL SECURITY ISSUE: Using fallback SECRET_KEY in Production mode!"
    )

# Automatic ALLOWED_HOSTS fallback for development
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# License Debug Bypass
LICENSE_DEBUG_BYPASS = env.bool("LICENSE_DEBUG_BYPASS", default=False)
BIMS_DEBUG_TIER = env("BIMS_DEBUG_TIER", default="ultra").lower()


# SECURITY: Production security settings (Consolidated for robustness)
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)

# SESSION/CSRF Cookies:
# If DEBUG=True (Dev) or a specific bypass is set, we allow insecure cookies for localhost testing.
# In a hardened build, these will usually be True unless SECURE_SSL_REDIRECT is False.
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)

# Standard Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = env("X_FRAME_OPTIONS", default="DENY")

# HSTS settings
SECURE_HSTS_SECONDS = env.int(
    "SECURE_HSTS_SECONDS", default=31536000 if SECURE_SSL_REDIRECT else 0
)
if SECURE_HSTS_SECONDS > 0:
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
    )
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "simple_history",
    # Local apps
    "apps.core",
    "apps.residents",
    "apps.certificates",
    "apps.blotter",
    "apps.business",
    "apps.finance",
    "apps.audit",
    "apps.gis",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "apps.core.middleware.setup.SetupRequiredMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.license.LicenseVerificationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",  # Audit trail
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom context processors
                "apps.core.context_processors.barangay_info",
                "apps.core.context_processors.user_info",
                "apps.core.context_processors.tier_info",
                "apps.core.context_processors.system_version",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Production-Grade System-Integrated Persistence
# All data is stored in a fixed system location for stability and easy backup
BIMS_DATA_ROOT = Path(env("BIMS_DATA_ROOT", default="C:/BIMS_Data"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BIMS_DATA_ROOT / "db.sqlite3"),
        "OPTIONS": {
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
    }
}
# Ensure the data directory exists
try:
    BIMS_DATA_ROOT.mkdir(parents=True, exist_ok=True)
except Exception:
    # Fallback for development/non-Windows systems
    BIMS_DATA_ROOT = BASE_DIR / "data"
    BIMS_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    DATABASES["default"]["NAME"] = str(BIMS_DATA_ROOT / "db.sqlite3")


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Manila"  # Philippine timezone

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
_prototype_static = BASE_DIR / "prototype" / "static"
if _prototype_static.exists():
    STATICFILES_DIRS.append(_prototype_static)

# WhiteNoise configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BIMS_DATA_ROOT / "media"

# Logging Configuration
LOGS_DIR = BIMS_DATA_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "app_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "info.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "errors.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
        },
        "security_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "security.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["security_file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": True,
        },
    },
}

# External Storage for Certificates (Safe from project deletion/temp cleanup)
BIMS_CERTIFICATE_STORAGE_ROOT = BIMS_DATA_ROOT / "certificates"
BIMS_CERTIFICATE_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication URLs
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:login"

# Custom user model
AUTH_USER_MODEL = "core.User"
