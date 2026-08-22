"""Django settings for the eye clinic management system."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in {"1", "true", "yes"}
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        from django.core.management.utils import get_random_secret_key

        SECRET_KEY = get_random_secret_key()
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be configured when DEBUG is disabled.")
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]

ARKESSEL_API_KEY = os.environ.get("ARKESSEL_API_KEY", "")
ARKESSEL_SENDER_ID = os.environ.get("ARKESSEL_SENDER_ID", "EyeClinic")
SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "arkesel")

TAILWIND_APP_NAME = "theme"
AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tailwind",
    "theme",
    "clinic",
    "patients",
    "dashboard",
    "appointment",
    "visits",
    "accounts",
]
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if DEBUG:
    MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

ROOT_URLCONF = "hospital_appoitment.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [
        BASE_DIR / "accounts" / "templates",
        BASE_DIR / "dashboard" / "templates",
        BASE_DIR / "appointment" / "templates",
        BASE_DIR / "templates",
    ],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "clinic.context_processors.clinic_configuration",
    ]},
}]
WSGI_APPLICATION = "hospital_appoitment.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.environ.get("DB_USER", ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Africa/Accra"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", str(not DEBUG)).lower() in {"1", "true", "yes"}
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "False").lower() in {"1", "true", "yes"}
SECURE_HSTS_PRELOAD = os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", "False").lower() in {"1", "true", "yes"}
X_FRAME_OPTIONS = "DENY"
