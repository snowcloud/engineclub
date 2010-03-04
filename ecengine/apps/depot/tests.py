"""
apps/depot/tests.py
"""

from django.conf import settings
from django.test import TestCase

from depot.models import Item, Location, load_item_data
from depot.forms import ShortItemForm
from mongoengine import connect

# *******   WARNING  *********
# mongoengine.connect not resetting the db, so tearDown would clear main DB
# settings_test sets MONGO_TESTING & is used to check connection to main DB is not set

class ItemTest(TestCase):
    
    def setUp(self):
        if not settings.MONGO_TESTING:
            raise Exception('must use ecengine.settings_test for these tests')
        connect('test_db', host='localhost', port=27017)
        
    def tearDown(self):
        Item.drop_collection()
        Location.drop_collection()

    def _load_data(self):
        """loads fixture data for test Items"""
        item_data = open('%s/apps/depot/fixtures/items.json' % settings.PROJECT_PATH, 'rU')
        load_item_data('item', item_data)
        item_data.close()
        item_data = open('%s/apps/depot/fixtures/locations.json' % settings.PROJECT_PATH, 'rU')
        db = load_item_data('location', item_data)
        item_data.close()
        return db

    def test_items(self):
        self._load_data()
        self.assertEqual(Item.objects.count(), 6)
        item = Item.objects.get(url='http://test.example.com/1/')
        self.assertEqual(item.url, 'http://test.example.com/1/')
        self.assertEqual(item.metadata.author, '1')
        
    def test_newitem(self):
        """
        Tests create a new item.
        """
        url = 'http://test.example.com/1/'
        title = 'test title'
        author = "1"
        item = Item.objects.get_or_create(url=url, defaults={'title': title})
        item.metadata.author = author
        self.assertEqual(item.url, url)
        self.assertEqual(item.title, title)
        self.assertEqual(item.metadata.author, author)
    
    def test_tags(self):
        """docstring for test_tags"""
        self._load_data()
        items = Item.objects(tags='red')
        # print [(i.title, i.tags) for i in Item.objects]
        # print 'red items: ', items
        self.assertEqual(len(items), 3)
        # 6 tags contain blue OR red
        items = Item.objects(tags__in=['blue', 'red'])
        self.assertEqual(len(items), 6)
        # 2 tags contain blue AND red
        items = Item.objects(tags__all=['blue', 'red'])
        self.assertEqual(len(items), 2)

    def test_geo(self):
        """docstring for test_geo"""
        
        db = self._load_data()
        db.eval('db.location.ensureIndex( { lat_lon : "2d" } )')
        self.assertEqual(Location.objects.count(), 1)
        eval_result = db.eval('db.runCommand( { geoNear : "location" , near : [50,-3], num : 10 } );')
        results = eval_result['results']
        locs = [res['obj'] for res in results]
        # print '\ndistance: ', res['dis'], res['obj']['name']
        self.assertEqual(locs[0]['name'], u'Gilmerton, Edinburgh, Scotland, GB')
        items = Item.objects(locations__in=[locs[0]['woeid']])
        self.assertEqual(len(items), 2)
        
    def test_form(self):
        """test form creation"""
        url = 'http://test.example.com/10/'
        title = 'test title'
        form = ShortItemForm({'url': url, 'title': title})
        self.assertTrue(form.is_valid())

