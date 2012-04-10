# -*- coding: utf-8 -*-
"""
apps/firebox/tests.py
"""

from django.test import TestCase, TransactionTestCase
# from firebox.ordnancesurvey import get_os_postcode, \
#     OS_LABEL, OS_TYPE, OS_LAT, OS_LON, OS_WARD, OS_DISTRICT, OS_COUNTRY
from firebox.views import *

from resources.forms import ShortResourceForm
from resources.models import Resource, Location, load_resource_data
from resources.search import lat_lon_to_str, get_location_for_postcode
from mongoengine import connect
from mongoengine.connection import _get_db as get_db

TEST_DB_NAME = 'test_db2'

# TEST_URL = "http://www.gilmerton.btik.com/p_Pilates.ikml"
TEST_URL = "http://www.gilmerton.btik.com/"
TEST_URL_RESULT = 3
TEST_URL2 = "http://www.anguscardiacgroup.co.uk/Programme.htm"
TEST_URL2_RESULT = 20

SEP = '**************'

def _print_db_info():
    """docstring for _print_db_info"""
    print SEP
    print 'Resource: ', Resource.objects.count()
    print 'Location: ', Location.objects.count()
    print SEP
    
# class PlacemakerTest(TransactionTestCase):
#     def test_url(self):
#         """
#         Tests that 3 places are found in page at TEST_URL.
#         """
#         g = geomaker(TEST_URL)
#         p = g.find_places()
#         print 'testing geomaker...'
#         if p.places:
#             print  p.geographic_scope
#             print  p.administrative_scope
#             for place in p.places:
#                 print '%s: %s, %s/%s - %s (%s)' % (place.placetype, place.name, place.centroid.latitude, place.centroid.longitude, place.woeid, place.confidence)
#         else:
#             print 'no places found'
        
#         self.assertEqual(len(p.places), TEST_URL_RESULT)

# class TermExtractorTest(TransactionTestCase):
#     """docstring for TermExtractorTest"""
#     def test_url(self):
#         terms = get_terms(TEST_URL2)
#         print terms
#         self.assertEqual(len(terms), TEST_URL2_RESULT)


class OSLocationTest(TransactionTestCase):
    """docstring for OSLocationTest"""
    def setUp(self):
        _print_db_info()

    def tearDown(self):
        _print_db_info()
        print 'dropping Resource and Location'
        Resource.drop_collection()
        # Location.drop_collection()
    
    def test_new_location(self):
        """
        http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR
        {
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://data.ordnancesurvey.co.uk/ontology/postcode/PostcodeUnit',
            'http://data.ordnancesurvey.co.uk/ontology/postcode/district': 'http://data.ordnancesurvey.co.uk/id/7000000000030505', 
            'http://data.ordnancesurvey.co.uk/ontology/postcode/country': 'http://data.ordnancesurvey.co.uk/id/country/scotland', 
            'http://data.ordnancesurvey.co.uk/ontology/postcode/ward': 'http://data.ordnancesurvey.co.uk/id/7000000000043410', 
            'http://www.w3.org/2003/01/geo/wgs84_pos#long': '-3.101903', 
            'http://www.w3.org/2003/01/geo/wgs84_pos#lat': '55.945354', 
            'http://www.w3.org/2000/01/rdf-schema#label': 'EH15 2QR'
            }
        Location:
            label = StringField(required=True)
            os_type = StringField(required=True)
            os_id = StringField(required=True)
            parents = ListField(ReferenceField(Location), default=list)
        
        """
        pc = 'AB35 5RB'
        # loc_id, result = get_os_postcode(pc, True)
        loc, created = get_location_for_postcode(postcode=pc)
        print created, loc.label, loc.lat_lon
        
        pc = 'AB35 xxx'
        # loc_id, result = get_os_postcode(pc, True)
        loc, created = get_location_for_postcode(postcode=pc)
        print created, loc.label, loc.lat_lon
        
        
        