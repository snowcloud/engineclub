"""
locations.tests
"""
from mongoengine.django.tests import MongoTestCase

from locations.models import Location

def setUpLocations(self):
    data = { "id" : "EH151AR", "accuracy" : "6", "postcode" : "EH15 1AR", "district" : "City of Edinburgh", "loc_type" : "POSTCODE", "country_code" : "SCT", "lat_lon" : [ 55.9539, -3.1164 ], "place_name" : "Portobello/Craigmillar, City of Edinburgh" }
    self.loc1 = Location.objects.create(**data)


class LocationTest(MongoTestCase):
    def setUp(self):
        setUpLocations(self)

    def test_locations(self):
    	self.assertEqual(Location.objects.count(), 1)