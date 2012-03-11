# -*- coding: utf-8 -*-
"""
depot/tests.py
"""

import os

from django.conf import settings
from django.contrib.auth.models import User
from mongoengine.connection import _get_db as get_db
from mongoengine.django.tests import MongoTestCase
from pysolr import Solr

from depot.models import Resource, Curation
from accounts.models import Account, Collection

SEP = '**************'
SOLR_ROWS = 5 # settings.SOLR_ROWS

def _dump_collections(collection_names=None):
    if collection_names is None:
        collection_names = [coll for coll in get_db().collection_names() if coll != 'system.indexes']
    for coll in collection_names:
        os.system('mongoexport -d {0} -c {1} -o output_{1}.json'.format(get_db().name, coll))

def _load_collections(collection_names=None, drop='--drop'):
    if collection_names is None:
        collection_names = [coll for coll in get_db().collection_names() if coll != 'system.indexes']
    for coll in collection_names:
        os.system('mongoimport -d {0} -c {1} --file output_{1}.json {2}'.format(get_db().name, coll, drop))

def _print_db_info():
    """docstring for _print_db_info"""
    print SEP
    print 'Account: ', Account.objects.count()
    print 'Membership: ', Membership.objects.count()
    print SEP

def _make_user(name):
    return User.objects.create_user(name, email="%s@example.com" % name, password='password')

def _make_resource(title, tags, owner):
    return  Resource.objects.create(title=title, tags=tags, owner=owner)

class ClassName(object):
    """docstring for ClassName"""
        
class TestBase(MongoTestCase):

    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__( *args, **kwargs)
        self.db_name =  get_db().name

    def setUp(self):
        # _print_db_info()
        self.user_bob = _make_user('bob')
        self.user_humph = _make_user('humph')
        self.user_jorph = _make_user('jorph')
        # self.user_group = _make_user('group')

        self.bob = Account.objects.create(name="Bob Hope", email="bob@example.com", local_id=str(self.user_bob.id))
        self.humph = Account.objects.create(name="Humph Floogerwhippel", email="humph@example.com", local_id=str(self.user_humph.id))
        self.jorph = Account.objects.create(name="Jorph Wheedjilli", email="jorph@example.com", local_id=str(self.user_jorph.id))

    def tearDown(self):
        # _print_db_info()
        pass
        

class CollectionsTest(TestBase):

    def test_collection(self):
        from firebox.views import reindex_resources

        # MAKE A COLLECTION
        coll1 = Collection.objects.create(name='Test Collection', owner=self.bob)
        coll2 = Collection.objects.create(name='Test Collection 2', owner=self.humph)
        self.assertEqual(1, Collection.objects(owner=self.bob).count())

        coll1.add_accounts([self.humph, self.jorph])
        coll1.add_accounts([self.humph])
        coll1.add_accounts([self.jorph])
        self.assertEqual(2, len(coll1.accounts))

        self.assertEqual(1, len(self.humph.collections))
        self.assertEqual(self.humph.collections[0].name, 'Test Collection')

        coll2.add_accounts([self.jorph])
        self.assertEqual(1, len(coll2.accounts))

        self.assertEqual(2, len(self.jorph.collections))
        # self.assertEqual(self.humph.collections[0].name, 'Test Collection')

        # MAKE SOME RESOURCES
        res1 = _make_resource('blah 1', ['blue', 'red'] ,self.humph)
        res2 = _make_resource('blah 2', ['green', 'red'] ,self.humph)
        res3 = _make_resource('blah 3', ['green', 'blue', 'red'] ,self.jorph)
        res4 = _make_resource('blah 4', ['green', 'red'] ,self.jorph)
        res5 = _make_resource('blah 5', ['green', 'yellow'] ,self.bob)
        res6 = _make_resource('blah 6', ['pink', 'red'] ,self.humph)
        res7 = _make_resource('blah 7', ['green', 'red'] ,self.bob)
        res8 = _make_resource('blah 8', ['yellow', 'red'] ,self.jorph)

        self.assertEqual(8, Resource.objects().count())
        self.assertEqual(3, Resource.objects(owner=self.humph).count())

        # TRY SOME SEARCHES
        reindex_resources(self.db_name, printit=False)
        conn = Solr(settings.SOLR_URL)
        kw = {'rows': SOLR_ROWS, 'fl': '*,score', 'qt': 'resources'}
        
        kwords = 'green'
        search_accts = [self.jorph, self.humph]
        kw['fq'] = 'accounts:(%s)'% ' OR '.join([str(ac.id) for ac in search_accts])
        results = conn.search(kwords, **kw)
        self.assertEqual(3, len(results))

        kwords = 'green'
        search_accts = [coll1]
        kw['fq'] = 'collections:(%s)'% ' OR '.join([str(ac.id) for ac in search_accts])
        results = conn.search(kwords, **kw)
        self.assertEqual(3, len(results))

        kwords = 'red'
        search_accts = [coll2]
        kw['fq'] = 'collections:(%s)'% ' OR '.join([str(ac.id) for ac in search_accts])
        results = conn.search(kwords, **kw)
        self.assertEqual(3, len(results))

        coll2.add_accounts([self.bob])
        self.assertEqual(2, len(coll2.accounts))
        
        Resource.reindex_for(self.bob)

        results = conn.search(kwords, **kw)
        self.assertEqual(4, len(results))

        res9 = _make_resource('blah 9', ['yellow', 'red'] ,self.bob)
        res9.save(reindex=True)
        results = conn.search(kwords, **kw)
        self.assertEqual(5, len(results))

