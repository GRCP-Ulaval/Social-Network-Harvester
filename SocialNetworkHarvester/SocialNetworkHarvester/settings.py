"""
Django settings for SocialNetworkHarvester project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import logging
import os
import socket

from .environment import (
    SECRET_KEY,
    DEBUG,
    FACEBOOK_APP_PARAMS,
    EMAIL_HOST,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_USE_SSL,
    EMAIL_PORT,
    DATABASE_PARAMS)
from .logger import Logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ['*']

LOGIN_URL = '/login_page'

# css class yetToCome produces an html layer on top of features that are not implemented yet. This hides them instead.
DISPLAY_YET_TO_COMES = False

# Change this value in production (can be wathever number) to force clients to clear their cached content
STATICFILES_VERSION = 1.0

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'SocialNetworkHarvester',
    'AspiraUser',
    'Facebook',
    'tool',
    'Twitter',
    'Youtube',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SocialNetworkHarvester.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, '/SocialNetworkHarvester/templates/'),
            os.path.join(BASE_DIR, '/AspiraUser/templates/'),
            os.path.join(BASE_DIR, '/Facebook/templates/'),
            os.path.join(BASE_DIR, '/tool/templates/'),
            os.path.join(BASE_DIR, '/Twitter/templates/'),
            os.path.join(BASE_DIR, '/Youtube/templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'SocialNetworkHarvester.context_processor.settings_variables'
            ],
        },
    },
]

WSGI_APPLICATION = 'SocialNetworkHarvester.wsgi.application'

DATABASES = {
    'default': {
        **DATABASE_PARAMS,
        'OPTIONS': {
            "charset": "utf8mb4"
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'staticfiles'),)

LOG_DIRECTORY = os.path.join(BASE_DIR, "log")

###### LOGERs ######
twitterLogger = Logger(loggerName='twitterLogger', filePath=os.path.join(LOG_DIRECTORY, "twitter.log"),
                       append=True, indentation=0, showThread=True)
facebookLogger = Logger(loggerName='facebookLogger', filePath=os.path.join(LOG_DIRECTORY, "facebook.log"),
                        append=True, indentation=0, showThread=False)
youtubeLogger = Logger(loggerName='youtubeLogger', filePath=os.path.join(LOG_DIRECTORY, "youtube.log"),
                       append=False, indentation=0, showThread=True)
viewsLogger = Logger(loggerName='viewsLogger', filePath=os.path.join(LOG_DIRECTORY, "views.log"),
                     append=True, indentation=2)