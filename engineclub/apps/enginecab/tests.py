# -*- coding: utf-8 -*-
"""
depot/tests.py
"""

import os

from django.contrib.auth.models import User
from mongoengine.connection import _get_db as get_db
from mongoengine.django.tests import MongoTestCase

from depot.models import Resource
from engine_groups.models import Account
from engine_groups.collections import Collection

SEP = '**************'

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

class TestBase(MongoTestCase):
    def setUp(self):
        # _print_db_info()
        self.user_humph = _make_user('bob')
        self.user_jorph = _make_user('jorph')
        self.user_group = _make_user('group')

        self.humph = Account.objects.create(name="Humph Floogerwhippel", email="humph@example.com", local_id=str(self.user_humph.id))
        self.jorph = Account.objects.create(name="Jorph Wheedjilli", email="jorph@example.com", local_id=str(self.user_jorph.id))
        # self.group = Account.objects.create(
        #     name="Flupping Baxters of Falkirk", 
        #     email="group@example.com", 
        #     local_id=str(self.user_group.id),
        #     )
        # self.group.add_member(self.humph)
        # self.group.add_member(self.jorph, role=ADMIN_ROLE)

    def tearDown(self):
        # _print_db_info()
        pass
        
        # _dump_accounts('blah.json')
        # print 'dropping Account docs'
        # Account.drop_collection()
        # Membership.drop_collection()

class CollectionsTest(TestBase):

    def test_collection(self):

        res1 = Resource.objects.create(
            title='blah', 
            tags=['blue', 'red'],
            author=self.humph
            )
        res2 = Resource.objects.create(
            title='blah 2', 
            tags=['green', 'red'],
            author=self.humph
            )
        res3 = Resource.objects.create(
            title='blah 3', 
            tags=['green', 'red'],
            author=self.jorph
            )
        self.assertEqual(3, Resource.objects().count())
        self.assertEqual(2, Resource.objects(owner=self.humph).count())

        c = Collection.objects.create(name='Test Collection', owner=self.humph)
        self.assertEqual(1, Collection.objects(owner=self.humph).count())

        
        
        