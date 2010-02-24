
from django.test import TestCase
from firebox.views import *

# TEST_URL = "http://www.gilmerton.btik.com/p_Pilates.ikml"
TEST_URL = "http://www.gilmerton.btik.com/"

class PlacemakerTest(TestCase):
    def test_url(self):
        """
        Tests that 3 places are found in page at TEST_URL.
        """
        p = geomaker(TEST_URL)
        print 'testing geomaker...'
        if p.places:
            print  p.geographic_scope
            print  p.administrative_scope
            for place in p.places:
                print '%s: %s, %s/%s - %s (%s)' % (place.placetype, place.name, place.centroid.latitude, place.centroid.longitude, place.woeid, place.confidence)
        else:
            print 'no places found'
        
        self.assertEqual(len(p.places), 3)

