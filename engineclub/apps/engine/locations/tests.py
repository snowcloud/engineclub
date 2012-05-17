"""
locations.tests
"""
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase
from ecutils.tests import MongoTestCase

from locations.models import Location

def setUpLocations(self):
    data = { "id" : "EH151AR", "accuracy" : "6", "postcode" : "EH15 1AR", "district" : "City of Edinburgh", "loc_type" : "POSTCODE", "country_code" : "SCT", "lat_lon" : [ 55.9539, -3.1164 ], "place_name" : "Portobello/Craigmillar, City of Edinburgh" }
    self.loc1 = Location.objects.create(**data)

    data = { "id" : "242935172", "accuracy" : "6", "country_code" : "SCT", "district" : "North Lanarkshire", "lat_lon" : [ 55.7720205, -3.9695229 ], "loc_type" : "OSM_PLACENAME", "place_name" : "Muirhouse" }
    self.loc2 = Location.objects.create(**data)

    data = { "id" : "33195942", "accuracy" : "6", "country_code" : "SCT", "district" : "City of Edinburgh", "lat_lon" : [ 55.9687743, -3.2607252 ], "loc_type" : "OSM_PLACENAME", "place_name" : "Muirhouse" }
    self.loc3 = Location.objects.create(**data)

    data = { "id" : "G40QR", "accuracy" : "6", "postcode" : "G4 0QR", "district" : "Glasgow City", "loc_type" : "POSTCODE", "country_code" : "SCT", "lat_lon" : [ 55.8607, -4.2397 ], "place_name" : "Anderston/City, Glasgow City" }
    self.loc4 = Location.objects.create(**data)

    data = { "id" : "G5", "accuracy" : 4, "country_code" : "SCT", "district" : "", "lat_lon" : [ 55.8432784, -4.245007699999999 ], "loc_type" : "POSTCODEDISTRICT", "place_name" : "Glasgow", "postcode" : "G5" }
    self.loc5 = Location.objects.create(**data)

class LocationTest(MongoTestCase):
    def setUp(self):
        setUpLocations(self)

    def test_locations(self):
        self.assertEqual(Location.objects.count(), 5)
