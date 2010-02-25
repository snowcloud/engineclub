# using this to get round a bug in mongoengine where setting connection doesn't change to test_db
# so live DB was cleared in testing teardown
# to use:
# export DJANGO_SETTINGS_MODULE=ecengine.settings_test
# django-admin.py test

from settings import *

