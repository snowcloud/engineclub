# Django settings for ecengine project.

import os
import sys
import logging

# logging.basicConfig(level=logging.WARNING,
#     format='%(asctime)s | %(levelname)s | %(message)s')

LOGGING = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s | %(levelname)s | %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            # 'filters': ['simple']
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'aliss': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            # 'filters': ['simple']
        }
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('your name', 'email@exmaple.com'),
)

CONTACT_EMAILS = MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'engineclubdb',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'TEST_NAME': 'testsqlitedb'
    }
}

LATLON_SEP= ', '

# set/override these in settings_local
# SOLR_URL = 'http://127.0.0.1:8983/solr'
SOLR_BATCH_SIZE = 100
SOLR_ROWS = 100
SOLR_LOC_BOOST_DEFAULT = 30.0
SOLR_LOC_BOOST_MAX = 100.0

STORY_TAG = '#aliss-story'

YAHOO_KEY = 'your_key_here...'

TIME_ZONE = 'Europe/London'
DATE_FORMAT='d M Y, H:i'
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps/cab"))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps/engine"))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps/firebox"))
# sys.path.insert(0, os.path.join(PROJECT_PATH, "libs"))

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'sitetemplates')
)

USE_I18N = True
# ADMIN_MEDIA_PREFIX = '/admin/media/'

SECRET_KEY = 'your_django_secret_key_here...'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

AUTHENTICATION_BACKENDS = (
    'accounts.backends.EngineGroupsBackend',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # "sitedown.middleware.SitedownMiddleware",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "issues.context_processors.message_stats",
)

ROOT_URLCONF = 'engineclub.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'accounts',
    'ecutils',
    'enginecab',
    'firebox',
    'locations',
    'resources',
    'youraliss',
    'contact_form',
    'sitedown',
    'issues',
    'invites',
    'home',
    'stories',

)
# override any of the above in your own settings_local.py
# put your secret keys in there
try:
    from settings_local import *
except ImportError:
    pass

