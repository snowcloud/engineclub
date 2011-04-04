# Django settings for ecengine project.

import os
import sys

_TESTING= 'test' in sys.argv

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
    }
}

# using this to get round a bug in mongoengine where setting connection doesn't change to test_db
# so live DB was cleared in testing teardown

try:
  MONGO_TESTING= 'test' in sys.argv
except KeyError:
  MONGO_TESTING=False

# MongoDBTestRunner creates/drops test db
# TEST_RUNNER = 'depot.tests.MongoDBTestRunner'

# MongoDBRunner uses current db
TEST_RUNNER = 'depot.tests.MongoDBRunner'

# repeated connects now fixed in mongoengine
from mongoengine import connect
MONGO_DB= 'test_db'
connect(MONGO_DB, host='localhost', port=27017)
LATLON_SEP= ', '

# set/override these in settings_local
# SOLR_URL = 'http://127.0.0.1:8983/solr'
SOLR_BATCH_SIZE = 100
SOLR_ROWS = 20

YAHOO_KEY = 'your_key_here...'

TIME_ZONE = 'Europe/London'
DATE_FORMAT='%d %B %Y, %H:%M'
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))
# sys.path.insert(0, os.path.join(PROJECT_PATH, "libs"))

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static')
TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'sitetemplates')
)

USE_I18N = True
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/admin/media/'
SECRET_KEY = 'ep1n==cyo=%%p#+aie!ixnuky&tnpwz8_7!i8ot^a()#--0ls3'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
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
    'home',
    'enginecab',
    'depot',
    'firebox',
    'ecutils',
    'contact_form',
    
)
# override any of the above in your own settings_local.py
try:
    from settings_local import *
except ImportError:
    pass

