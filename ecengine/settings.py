# Django settings for ecengine project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('your name', 'email@exmaple.com'),
)

CONTACT_EMAILS = MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'engineclub',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#mongoDB settings
from mongoengine import connect
connect('aliss', host='localhost', port=27017)


TIME_ZONE = 'Europe/London'
DATE_FORMAT='%d %B %Y, %H:%M'
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

from os import path as os_path
PROJECT_PATH = os_path.abspath(os_path.split(__file__)[0])

MEDIA_ROOT = os_path.join(PROJECT_PATH, 'static')
TEMPLATE_DIRS = (
    os_path.join(PROJECT_PATH, 'sitetemplates')
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

ROOT_URLCONF = 'ecengine.urls'

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
    'apps.aliss',
    'apps.enginecab',
    'apps.depot',
    'apps.firebox',
    'apps.ecutils',
    'contact_form',
    
)
# override any of the above in your own settings_local.py
try:
    from settings_local import *
except ImportError:
    pass

