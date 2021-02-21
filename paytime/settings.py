"""
Django settings for paytime project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from __future__ import absolute_import

import os
import sys
from pathlib import Path

import django_heroku
from celery.schedules import crontab
from django.contrib import messages
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, "", ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", False)

ALLOWED_HOSTS = ["pay-time.herokuapp.com/", "127.0.0.1"]

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "authentication",
    "auditing",
    "dashboard",
    "user",
    "finance",
    "django_celery_beat",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "paytime.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        "APP": {
            "client_id": "467773689793-qau0m5seubukpbp8u7jqco0n7ot3h1fo.apps.googleusercontent.com",
            "secret": "tQ6sK4h_hOXf-hlagFz8wyg-",
            "key": "",
        }
    }
}

# Django Allauth configurations
# https://django-allauth.readthedocs.io/en/latest/advanced.html#custom-user-models
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
LOGIN_REDIRECT_URL = "/dashboard"
LOGIN_URL = "/accounts/login/"
ACCOUNT_FORMS = {"signup": "authentication.forms.SignupForm"}
if not DEBUG:
    # if set to "mandatory",
    # ACCOUNT_EMAIL_REQUIRED must be set to True
    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
else:
    pass
    # ACCOUNT_EMAIL_VERIFICATION = "optional"
    if TESTING:
        ACCOUNT_EMAIL_VERIFICATION = "optional"
    else:
        ACCOUNT_EMAIL_VERIFICATION = "mandatory"

WSGI_APPLICATION = "paytime.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "paytime2"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PASSWORD": os.getenv("DB_PASSWORD", "password"),
        "USER": os.getenv("DB_USER", "comfy"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "UTC"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
# MEDIA_ROOT = "/deploy/paytime/media"
# https://data-flair.training/blogs/django-file-upload/

# This is the URL the user can go to and upload their files from the browser
MEDIA_URL = "/media/"

# Tells Django to store all the uploaded files in a folder called ’media’
# created in the BASE_DIR, i.e., the project Directory
# therefore we need to create a folder called media in the root
# of this project, on the same level as manage.py
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "paytime/static")]
STATICFILES_STORAGE = "whitenoise.django.GzipManifestStaticFilesStorage"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s [%(process)d] [%(levelname)s] "
                + "pathname=%(pathname)s lineno=%(lineno)s "
                + "funcname=%(funcName)s %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "testlogger": {
            "handlers": ["console"],
            "level": "INFO",
        }
    },
}

django_heroku.settings(locals(), logging=False)

# tell django which model to use as user model
AUTH_USER_MODEL = "user.User"

# check this sites for precommit setup
# https://pre-commit.com/
# https://ljvmiranda921.github.io/notebook/2018/06/21/precommits-using-black-and-flake8/

# sometimes google if used as the smtp provider can
# block ip addresses of app, check here
# https://stackoverflow.com/a/29125232/8536024
EMAIL_HOST = "smtp.gmail.com"
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else os.environ.get("EMAIL_BACKEND")
)
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]

MESSAGE_TAGS = {
    # since django returns error, and we want to
    # map error to danger in messages
    # so we would be able to properly configure
    # bootstrap alert with the right classes
    messages.ERROR: "danger"
}

# django-ratelimit returns a 403 by default. We define our own view to instead
# return a {status_code}}.
# RATELIMIT_VIEW = "{application_name}.views.{method/function_name}"

PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")


# Celery Configuration Options
CELERY_BROKER_URL = "redis://:pbc8499a36cba21e10f3e646c5e320c3c0509838cb9cd8cf977b6d3d5863b9be7@ec2-34-203-49-113.compute-1.amazonaws.com:26029"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_BEAT_SCHEDULE = {
    # start the celery beat with
    # celery -A paytime beat -l INFO
    # start celery with
    # celery -A paytime worker -l info p
    "ordinary-taks": {
        "task": "dashboard.tasks.sleepy",
        "schedule": 5.0,
    },
}
# CELERY_TIMEZONE = "UTC"
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60
