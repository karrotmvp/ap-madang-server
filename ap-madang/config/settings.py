"""
Django settings for ap-madang project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from sentry_sdk.integrations.django import DjangoIntegration
import sentry_sdk
from pathlib import Path
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!

if os.environ.get("DEBUG") == "False":
    DEBUG = False
else:
    DEBUG = True

ENV_NAME = os.environ.get("ENV_NAME")

if DEBUG or ENV_NAME in ["dev", "dev-sub"]:
    ALLOWED_HOSTS = ["*"]

else:
    ALLOWED_HOSTS = [
        "server.daangn-meetup.com",
        "121.166.172.250",
        "127.0.0.1",
        "localhost",
        ".ap-northeast-2.compute.amazonaws.com",
        "ap-madang-env.eba-rtbc3esy.ap-northeast-2.elasticbeanstalk.com",
        "ap-madang-env-sub.eba-rtbc3esy.ap-northeast-2.elasticbeanstalk.com",
        "ec2-15-165-246-184.ap-northeast-2.compute.amazonaws.com"
        "d2p80xtunaym1x.cloudfront.net",
        "dtm2ixz1i9ezl.cloudfront.net",
        "meeting.daangn-meetup.com",
        "shorturl.daangn-meetup.com",
    ]


# Application definition
THIRD_PARTY_APPS = [
    "rest_framework",
    "drf_yasg",
    "corsheaders",
    "django_crontab",
    "storages",
    # "debug_toolbar",
]

CUSTOM_APPS = [
    "reservation",
    "oauth",
    "user",
    "meeting",
    "alarmtalk",
    "support",
    "agora",
    "share",
]

INSTALLED_APPS = (
    CUSTOM_APPS
    + THIRD_PARTY_APPS
    + [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
)

# Cron
if DEBUG or ENV_NAME in ["cron", "cron-dev"]:
    CRONJOBS = [
        # ("*/5 * * * *", "meeting.cron.add_fake_cnt", ">> /var/log/add_fake_cnt.log"),
        (
            "*/30 * * * *",
            "alarmtalk.cron.send_meeting_alarm",
            ">> /var/log/crontab_meeting_alarm.log",
        ),
        (
            "0 1 * * *",
            "meeting.cron.create_tomorrows_meeting",
            ">> /var/log/crontab_create_tomorrows_meeting.log",
        ),
        (
            "0 0 1 1 *",
            "agora.cron.update_agora_user_list",
            ">> /var/log/crontab_update_agora_user_list.log",
        ),
    ]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# INTERNAL_IPS = ["127.0.0.1"]

# CORS
if DEBUG or ENV_NAME in ["dev", "dev-sub"]:
    CORS_ORIGIN_ALLOW_ALL = True

else:
    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGIN_REGEXES = CORS_ORIGIN_WHITELIST = [
        "http://localhost:3000",
        "http://192.168.60.184:3000",
        "https://d2p80xtunaym1x.cloudfront.net",
        "http://d2p80xtunaym1x.cloudfront.net",
        "https://dtm2ixz1i9ezl.cloudfront.net",
        "http://dtm2ixz1i9ezl.cloudfront.net",
        "https://meeting.daangn-meetup.com",
    ]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_LOCAL_NAME"),
            "USER": os.environ.get("DB_LOCAL_USER"),
            "PASSWORD": os.environ.get("DB_LOCAL_PASSWORD"),
            "HOST": os.environ.get("DB_LOCAL_HOST"),
            "PORT": os.environ.get("DB_LOCAL_PORT"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_PROD_NAME"),
            "USER": os.environ.get("DB_PROD_USER"),
            "PASSWORD": os.environ.get("DB_PROD_PASSWORD"),
            "HOST": os.environ.get("DB_PROD_HOST"),
            "PORT": os.environ.get("DB_PROD_PORT"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }

if DEBUG:
    LOGGING = {
        "version": 1,
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "filters": ["require_debug_true"],
                "class": "logging.StreamHandler",
            }
        },
        "loggers": {
            "django.db.backends": {
                "level": "DEBUG",
                "handlers": ["console"],
            }
        },
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


if ENV_NAME != "Local":
    sentry_sdk.init(
        dsn="https://b8ef20910ff44060b06a7b9123637ce3@o1046587.ingest.sentry.io/6025026",
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        environment=ENV_NAME,
    )

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "ap-madang-server"
AWS_S3_REGION_NAME = "ap-northeast-2"

AWS_S3_CUSTOM_DOMAIN = "%s.s3.%s.amazonaws.com" % (
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME,
)
DEFAULT_FILE_STORAGE = "config.custom_storages.S3DefaultStorage"
STATICFILES_STORAGE = "config.custom_storages.S3StaticStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


APP_ID_SECRET = os.environ.get("APP_ID_SECRET")
API_KEY = os.environ.get("API_KEY")
BASE_URL_REGION = os.environ.get("BASE_URL_REGION")
BASE_URL_OAUTH = os.environ.get("BASE_URL_OAUTH")
JWT_SECRET = os.environ.get("JWT_SECRET")
CLIENT_BASE_URL = os.environ.get("CLIENT_BASE_URL")
AGORA_APP_ID = os.environ.get("AGORA_APP_ID")
AGORA_APP_CERTIFICATE = os.environ.get("AGORA_APP_CERTIFICATE")
ZOOM_API_KEY = os.environ.get("ZOOM_API_KEY")
ZOOM_API_SECRET = os.environ.get("ZOOM_API_SECRET")
SERVER_SHORT_URL_BASE_URL = os.environ.get("SERVER_SHORT_URL_BASE_URL")
MEETING_CREATE_SLACK_WEBHOOK_URL = os.environ.get("MEETING_CREATE_SLACK_WEBHOOK_URL")
IMAGE_RESIZE_SQS_URL = os.environ.get("IMAGE_RESIZE_SQS_URL")
AGORA_CUSTOMER_ID = os.environ.get("AGORA_CUSTOMER_ID")
AGORA_CUSTOMER_SECRET = os.environ.get("AGORA_CUSTOMER_SECRET")
MEETING_ENTER_SLACK_WEBHOOK_URL = os.environ.get("MEETING_ENTER_SLACK_WEBHOOK_URL")
ERROR_SLACK_WEBHOOK_URL = os.environ.get("ERROR_SLACK_WEBHOOK_URL")
