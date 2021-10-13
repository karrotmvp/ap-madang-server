"""
Django settings for ap-madang project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!

if os.environ.get('DEBUG') == 'False':
    DEBUG = False
else: 
    DEBUG = True

ALLOWED_HOSTS = [
    '*',
    '121.166.172.250',
    '127.0.0.1',
    'localhost',
    '.ap-northeast-2.compute.amazonaws.com',
    'ap-madang-env.eba-rtbc3esy.ap-northeast-2.elasticbeanstalk.com',
    'd2p80xtunaym1x.cloudfront.net',
    'dtm2ixz1i9ezl.cloudfront.net'
]


# Application definition

INSTALLED_APPS = [
    'reservation',
    'oauth',
    'user',
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGIN_REGEXES = CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://192.168.60.184:3000',
    'https://d2p80xtunaym1x.cloudfront.net',
    'http://d2p80xtunaym1x.cloudfront.net',
    'https://dtm2ixz1i9ezl.cloudfront.net',
    'http://dtm2ixz1i9ezl.cloudfront.net'
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
      "default" : {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get('DB_LOCAL_NAME'),
        "USER": os.environ.get('DB_LOCAL_USER'),             
        "PASSWORD": os.environ.get('DB_LOCAL_PASSWORD'),
        "HOST": os.environ.get('DB_LOCAL_HOST'),
        "PORT": os.environ.get('DB_LOCAL_PORT')              
      }
    }
else :
    DATABASES = {
      "default" : {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get('DB_PROD_NAME'),
        "USER": os.environ.get('DB_PROD_USER'),             
        "PASSWORD": os.environ.get('DB_PROD_PASSWORD'),
        "HOST": os.environ.get('DB_PROD_HOST'),
        "PORT": os.environ.get('DB_PROD_PORT')              
      }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


APP_ID_SECRET = os.environ.get('APP_ID_SECRET')
API_KEY = os.environ.get('API_KEY')
BASE_URL_REGION = os.environ.get('BASE_URL_REGION')
BASE_URL_OAUTH = os.environ.get('BASE_URL_OAUTH')