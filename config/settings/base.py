"""
Base settings for BIMS2 project.
"""

import copy
import environ
from pathlib import Path
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Read .env file if it exists
ENV_FILE = BASE_DIR / '.env'
if ENV_FILE.exists():
    environ.Env.read_env(str(ENV_FILE))

# System Versioning
VERSION_FILE = BASE_DIR / 'VERSION'
if VERSION_FILE.exists():
    with open(VERSION_FILE, 'r') as f:
        BIMS_VERSION = f.read().strip()
else:
    BIMS_VERSION = '1.0.0-dev'


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-fallback-key-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# SECURITY: Production security settings
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=not DEBUG)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=not DEBUG)

# HSTS settings (only if SSL redirect is on)
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
    SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'simple_history',
    
    # Local apps
    'apps.core',
    'apps.residents',
    'apps.certificates',
    'apps.blotter',
    'apps.business',
    'apps.finance',
    'apps.audit',
    'apps.gis',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'apps.core.middleware.setup.SetupRequiredMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.license.LicenseVerificationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',  # Audit trail
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom context processors
                'apps.core.context_processors.barangay_info',
                'apps.core.context_processors.user_info',
                'apps.core.context_processors.tier_info',
                'apps.core.context_processors.system_version',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'  # Philippine timezone

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
_prototype_static = BASE_DIR / 'prototype' / 'static'
if _prototype_static.exists():
    STATICFILES_DIRS.append(_prototype_static)

# WhiteNoise configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Logging Configuration
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = copy.deepcopy(DEFAULT_LOGGING)

# Add our custom rotating file handler for production errors
LOGGING['handlers']['file'] = {
    'level': 'ERROR',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': LOGS_DIR / 'bims2.log',
    'maxBytes': 1024 * 1024 * 5,  # 5 MB
    'backupCount': 5,
    'formatter': 'verbose',
}

# Add verbose formatter
LOGGING['formatters']['verbose'] = {
    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
    'style': '{',
}

# Attach to the main django logger without removing existing (console) handlers
if 'django' not in LOGGING['loggers']:
    LOGGING['loggers']['django'] = {'handlers': [], 'level': 'INFO', 'propagate': True}

LOGGING['loggers']['django']['handlers'].append('file')

# Support app-level logging
LOGGING['loggers']['apps'] = {
    'handlers': ['console', 'file'] if DEBUG else ['file'],
    'level': 'DEBUG' if DEBUG else 'INFO',
    'propagate': True,
}

# External Storage for Certificates (Safe from project deletion/temp cleanup)
# FALLBACK: If DEBUG=True and no storage root is set, save to project media.
_default_storage = MEDIA_ROOT / 'certificates' / 'issued'
BIMS_CERTIFICATE_STORAGE_ROOT = env('BIMS_CERTIFICATE_STORAGE_ROOT', default=str(_default_storage))

# If it's a relative path or empty in DEBUG mode, ensure it's absolute within MEDIA_ROOT
if DEBUG and (not BIMS_CERTIFICATE_STORAGE_ROOT or BIMS_CERTIFICATE_STORAGE_ROOT == str(_default_storage)):
    BIMS_CERTIFICATE_STORAGE_ROOT = _default_storage
else:
    BIMS_CERTIFICATE_STORAGE_ROOT = Path(BIMS_CERTIFICATE_STORAGE_ROOT)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:login'

# Custom user model
AUTH_USER_MODEL = 'core.User'
