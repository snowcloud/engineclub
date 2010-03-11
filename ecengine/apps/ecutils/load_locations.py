import sys, os
sys.path.append('/Users/derek/dev_django')
sys.path.append('/Users/derek/dev_django/external_apps')
from django.core.management import setup_environ

from ecengine import settings_test
setup_environ(settings_test)


from depot.models import Location, load_item_data

def _load_data(self):
	"""loads fixture data for test Items"""
	item_data = open('%s/apps/depot/fixtures/items.json' % settings.PROJECT_PATH, 'rU')
	load_item_data('item', item_data)
	item_data.close()
	item_data = open('%s/apps/depot/fixtures/locations.json' % settings.PROJECT_PATH, 'rU')
	db = load_item_data('location', item_data)
	item_data.close()
	return db


existing_locs = [loc.woeid for loc in Location.objects]

print existing_locs





