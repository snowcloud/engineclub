# -*- coding: utf-8 -*-
"""
apps/depot/tests.py
"""

from django.conf import settings
from mongoengine.django.tests import MongoTestCase

from depot.models import Resource, Curation, Location, load_resource_data
from depot.search import lat_lon_to_str
from depot.forms import ShortResourceForm


# from mongoengine import connect
# from mongoengine.connection import _get_db as get_db

# from accounts.models import Account, get_account
# from pymongo.objectid import ObjectId

# import re

# from django.test.simple import *
# from django.test import TransactionTestCase

# TEST_DB_NAME = 'test_db2'
# DB_NAME = 'aliss'
# SOLR_URL = 'http://127.0.0.1:8983/solr'
# # SOLR_URL = settings.SOLR_URL
# SOLR_ROWS = 5 # settings.SOLR_ROWS

# TEST_LOCS = {
#     'ellon': '57.365287, -2.070642',
#     'peterheid': '57.584806, -1.875630',
#     'keith': '57.7036280142534, -2.85720247750133',
#     'carnoustie': '56.503836, -2.699406',
#     'downing st': '51.503541, -0.127670' # SW1A 2AA
# }

def _load_data(resources='resources', locations='locations'):
    """loads fixture data for test Resources"""
    resource_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, resources), 'rU')
    load_resource_data('resource', resource_data)
    resource_data.close()
    # print Resource.objects.count()
    # for resource in Resource.objects:
    #     resource.save()
    # print Resource.objects.count()
    
    
    # for resource in Resource.objects:
    #     locs = []
    #     for loc in resource.locations:
    #         print 'r'
    #     resource.locations = locs
    #     resource.save()
    #
    
    # no Locations while we refactor them
    
    # resource_data = open('%s/apps/depot/fixtures/%s.json' % (settings.PROJECT_PATH, locations), 'rU')
    # load_resource_data('location', resource_data)
    # resource_data.close()
    
# class MongoDBTestRunner(DjangoTestSuiteRunner):
#     def setup_databases(self, **kwargs):
#         db_name = TEST_DB_NAME
#         connect(db_name)
#         print 'Creating test-databasey: ' + db_name
#         _load_data()
#         return super(MongoDBTestRunner, self).setup_databases(**kwargs)

#     def teardown_databases(self, db_name, **kwargs):
#         from pymongo import Connection
#         conn = Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
#         conn.drop_database(db_name)
#         print 'Dropping test-databasey: ' + db_name
#         super(teardown_databases, self).setup_databases(db_name, **kwargs)

# class MongoDBRunner(DjangoTestSuiteRunner):
#     def setup_databases(self, **kwargs):
#         db_name = DB_NAME
#         connect(db_name)
#         print 'Using test_db: ' + db_name
#         # _load_data()
#         return super(MongoDBRunner, self).setup_databases(**kwargs)

#     def teardown_databases(self, db, **kwargs):
#         # from pymongo import Connection
#         # conn = Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
#         # conn.drop_database(db_name)
#         print 'Closing test-db: ', db[0][0][1], ' (data intact)'
#         super(MongoDBRunner, self).teardown_databases(db, **kwargs)

def makeResource(data):
    return Resource.objects.create(
        title=title,
        owner=owner)

def setUpResources(self):
    
    for idx, data in enumerate((
            {'title': 'title 0', 'owner': self.alice, 'tags': ['red', 'blue']},
            {'title': 'title 1', 'owner': self.alice, 'tags': ['blue', 'green']},
            {'title': 'title 2', 'owner': self.alice, 'tags': ['red', 'blue', 'green']},
            {'title': 'title 3', 'owner': self.bob, 'tags': ['red']},
            {'title': 'title 4', 'owner': self.jorph, 'tags': ['blue', 'green']},
            {'title': 'title 5', 'owner': self.jorph, 'tags': ['red', 'blue']},
            {'title': 'title 6', 'owner': self.hugo, 'tags': ['blue']},
            {'title': 'title 7', 'owner': self.group, 'tags': ['blue']},
            {'title': 'title 8', 'owner': self.group, 'tags': ['blue']},
            )):
        res =  Resource.objects.create(**data)
        setattr(self, 'resource%s' % idx, res)

class ResourceTest(MongoTestCase):
            
    def setUp(self):
        from accounts.tests import setUpAccounts
        setUpAccounts(self)
        setUpResources(self)

    def test_resources(self):
        self.assertEqual(Resource.objects.count(), 9)
        
    def test_newresource(self):
        """
        Tests create a new resource.
        """
        # uri = u'http://test.example.com/1/'
        title = u'test title 7'
        author = self.emma
        resource, created = Resource.objects.get_or_create(__raw__={'_id': u'4d135708e999fb30d8000007'}, defaults={'title': title, 'owner': author})
        resource.item_metadata.author = author
        self.assertTrue(created)
        # self.assertEqual(unicode(resource.id), u'4d135708e999fb30d8000001')
        self.assertEqual(resource.title, title)
        self.assertEqual(resource.item_metadata.author, author)
    
    def test_tags(self):
        """docstring for test_tags"""

        resources = Resource.objects(tags='red')
        self.assertEqual(len(resources), 4)
        # 6 tags contain blue OR red
        resources = Resource.objects(tags__in=['blue', 'red'])
        self.assertEqual(len(resources), 9)
        # 2 tags contain blue AND red
        resources = Resource.objects(tags__all=['blue', 'red'])
        self.assertEqual(len(resources), 3)
    
#     def test_tagslist(self):
#         """docstring for test_tagslist"""
#         # self.db = self._load_data()
#         self.assertEqual(Resource.objects.count(), 6)
#         for resource in Resource.objects:
#             resource.make_keys([])
#             resource.save()
#         update_keyword_index()
#         self.assertEqual(Resource.objects.count(), 6)
#         results = get_db().keyword.find( { "_id" : re.compile('^Bl*', re.IGNORECASE)} ) #.count()
#         self.assertEqual([i['_id'] for i in results], [u'blue'])
      
#     def test_geo(self):
#         """docstring for test_geo"""
#         # db = self._load_data()
#         self.assertEqual(Resource.objects.count(), 6)
#         for resource in Resource.objects:
#             resource.make_keys([])
#             resource.save()
#             # this is making a second object
#             # SEE EVERNOTE- PROB IF USING STRING AS ID- USE OBJECTID
#         update_keyword_index()
#         results = get_nearest('50', -3.00, categories=['blue']) # takes float or string for lat, lon
#         print results
#         for r in results[0]['resources']:
#             print r.title, r.tags, r.index_keys
#         self.assertEqual(Resource.objects.count(), 6)
#         self.assertEqual(len(results), 1)
#         self.assertEqual(len(results[0]['resources']), 1)





# from pysolr import Solr

# class SearchTest(TransactionTestCase):
    
#     # def test_load_resources(self):
#     #     print 'SHOULDN\'T BE IN HERE'
#     #     conn = Solr(settings.SOLR_URL)
#     #     conn.delete(q='*:*')
#     #     
#     #     for r in Resource.objects:
#     #     #     TODO: SEEMS TO PUT A LIST IN id ???  [u'234lj342lj23l12j3414']
#     #         doc = {'id': unicode(r.id), 'res_id': unicode(r.id), 'title': r.title, 'description': r.description, 'keywords': r.index_keys}
#     #         # print '%s %s' % (doc['res_id'], unicode(r.id)), r.id
#     #         locs = r.get_locations()
#     #         if locs:
#     #             # print '%s, %s' % (locs[0].latitude, locs[0].longitude)
#     #             doc['pt_location'] = '%s, %s' % (locs[0].latitude, locs[0].longitude)
#     #         conn.add([doc])
#     #         # print doc

#     def _rebuild_index(self, conn):
#         """docstring for rebuild_index"""
        
#         print "CLEARING INDEX..."
#         conn.delete(q='*:*')
#         print 'Indexing %s Resources...' % Resource.objects.count()
#         for res in Resource.objects:
#             res.index(conn)
        
    
#     def test_test(self):
#         # print 'starting solr test'
#         conn = Solr(SOLR_URL)
        
#         # self._rebuild_index(conn)
        
        
#         ellon = '57.365287, -2.070642'
#         peterheid = '57.584806, -1.875630'
#         keith = '57.7036280142534, -2.85720247750133'
#         loc = keith
#         print '\n\n*** keith ', loc
#         srch = '"mental health"'
#         # search(self, q, **kwargs)
        
#         kw = { 'sfield': 'pt_location', 'pt': loc, 'sort': 'geodist() asc', 'fl': '*,score' }
#         # kw = { 'fq':'{!geofilt pt=55.8,-3.10 sfield=store d=50}' }

#         results = conn.search(srch, **kw)
#         print '\n--\nsearch on [%s] : %s' % (srch, loc)
#         for result in results:
#             print '-', result['res_id'], result['score'], result['title'], result['pt_location']
        
#     def test_postcode(self):
#         conn = Solr(SOLR_URL)
        
#         aberdeen = 'Ab10 1AX'
#         # peterheid = '57.584806, -1.875630'
#         # keith = '57.7036280142534, -2.85720247750133'
#         print '\n\n*** aberdeen', aberdeen
#         loc = get_place_for_postcode(aberdeen, DB_NAME)
#         print loc
#         srch = '"mental health"'
#         # search(self, q, **kwargs)
        
#         kw = { 'sfield': 'pt_location', 'pt': lat_lon_to_str(loc['lat_lon']), 'sort': 'geodist() asc', 'fl': '*,score' }
#         # kw = { 'fq':'{!geofilt pt=55.8,-3.10 sfield=store d=50}' }

#         results = conn.search(srch, **kw)
#         print '\n--\nsearch on [%s] : %s' % (srch, loc['lat_lon'])
#         for result in results:
#             print '-', result['score'], result['title'], result['pt_location']
    
#     def test_dismax(self):
#         """docstring for test_dismax"""

#         conn = Solr(SOLR_URL)
        
#         kwords = 'dance'
#         kw = {
#             'rows': SOLR_ROWS,
#             'fl': '*,score',
#             'qt': 'resources',
#         }
        
#         results = conn.search(kwords, **kw)

#         print '\n--\nsearch on [%s] : ' % (kwords)
#         for result in results:
#             print '-', result['score'], result['title'] #, result['pt_location']

#     def test_dismax_events(self):
#         """docstring for test_dismax"""

#         conn = Solr(SOLR_URL)
        
#         # kwords = 'dance, music'
#         kwords = ''

#         kw = {
#             'rows': SOLR_ROWS,
#             'fl': '*,score',
#             'qt': 'resources',
#             # 'fq': '(event_start:[NOW/DAY TO *] OR event_end:[NOW/DAY TO *]) AND accounts:4d9b99d889cb16665c000000'
#             'fq': '(event_start:[NOW/DAY TO *] OR event_end:[NOW/DAY TO *])'
#         }
#         # a_type:2 AND a_begin_date:[1990-01-01T00:00:00.000Z TO 1999-12-31T24:59:99.999Z]
#         # regex to check date formats
#         # and check 1 < 2
#         results = conn.search(kwords, **kw)

#         print '\n--\nsearch on [%s] : ' % (kwords)
#         for result in results:
#             print '-', result['score'], result['title'], ', ', result.get('event_start', '-'), result.get('event_end', '-')
        
#     def test_dismax_loc(self):
#         """docstring for test_dismax"""

#         conn = Solr(SOLR_URL)

#         loc_name = 'downing st'
#         loc = TEST_LOCS[loc_name]
#         print '\n\n*** %s ' % loc_name, loc
    
#         kwords = 'heart'
#         kw = {
#             'rows': SOLR_ROWS,
#             'fl': '*,score',
#             'qt': 'resources',
#             'sfield': 'pt_location',
#             'pt': loc,
#             'bf': 'recip(geodist(),2,200,20)^20',
#             'sort': 'score desc',
#         }
    
#         results = conn.search(kwords, **kw)

#         print '\n--\nsearch on [%s] : ' % (kwords)
#         for result in results:
#             print '-', result['score'], result['title'], result.get('pt_location', '')
    
#     def test_curations(self):
#         """docstring for test_curations"""
        
        
#         acct = Account.objects.get(name="Derek Hoy")
#         print acct, acct.id
        
#         print list(Resource.objects(curations__owner=acct))
        
        
#         curations = Curation.objects(owner=acct).order_by('-item_metadata__last_modified')
        
#         for c in curations:
#             print c.owner, c.item_metadata.last_modified,  c.resource.title
        
#         # for c in Curation.objects.all():
#         #     if c.resource is None:
#         #         print '***', c.delete()
        
#         # see query option in map_reduce - http://www.mongodb.org/display/DOCS/MapReduce
#         # { "author.name" : "joe" }
        
#         # from bson.code import Code
#         # map = """
#         #     function() {
#         #         this.curations.forEach(function(c) {
#         #             x = {'owner': (c.owner.$id), 'lastmod': c.item_metadata.last_modified}
#         #             emit(x, 1);
#         #         })
#         #     }
#         # """ 
#         # map2 = """
#         #     function() {
#         #             emit(this, 1);
#         #     }
#         # """ 
#         # # print map
#         # reduce = """
#         #     function(key, values) {
#         #     var total = 0;
#         #     for(var i=0; i<values.length; i++) {
#         #     total += values[i];
#         #     }
#         #     return total;
#         #     }
#         # """
#         # # print reduce
#         # 
#         # from pymongo import Connection
#         # db = Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)['test_db']
#         # # print db, db.resources
#         # print db.resource.count()
#         # 
#         # result = db.resource.map_reduce(map, reduce, "myresults")
#         # 
#         # print 'results: ', [doc for doc in list(result.find())[:10] if doc['_id']['owner'] == acct.id]
        
#         # 
#         # 
#         # # # run a map/reduce operation spanning all posts
#         # results = Resource.objects(curations__owner=acct)[:2].map_reduce(map_f, reduce_f)
#         # results = list(results)
#         # print results
#         # self.assertEqual(len(results), 4)
#         # 
#         # music = filter(lambda r: r.key == "music", results)[0]
#         # self.assertEqual(music.value, 2)
#         # 
#         # film = filter(lambda r: r.key == "film", results)[0]
#         # self.assertEqual(film.value, 3)
#         # 
#         # BlogPost.drop_collection()




# #     # def test_form(self):
# #     #   """test form creation"""
# #     #   uri = 'http://test.example.com/10/'
# #     #   title = 'test title'
# #     #   form = ShortResourceForm({'uri': uri, 'title': title})
# #     #   self.assertTrue(form.is_valid())
    
# # class BigResourceTest(TransactionTestCase):
# #     
# # 
# #     def setUp(self):
# #         # test for and load big db
# #         if Resource.objects.count() == 0:
# #             self.db = _load_data('resources')
# # 
# #     # def test_test(self):
# #     #     print 'hello'
# # 
# #     def test_resources(self):
# #         title = u'title 2'
# #         url = u'http://test.example.com/2/'
# #         self.assertEqual(Resource.objects.count(), 6)
# #         resource = Resource.objects.get(__raw__={'_id': u'4d135708e999fb30d8000001'})
# #         self.assertEqual(resource.id, u'4d135708e999fb30d8000001')
# #         self.assertEqual(resource.item_metadata.author, u'1')
# #         # get an resource with a resource with this url
# #         # resources could share a url ?
# #         # resource = Resource.objects.get(resources__url=url)
# #         # self.assertEqual(resource.title, title)

    
    
    
