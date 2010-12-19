
from django.test import TestCase
from firebox.views import *

# TEST_URL = "http://www.gilmerton.btik.com/p_Pilates.ikml"
TEST_URL = "http://www.gilmerton.btik.com/"
TEST_URL_RESULT = 3
TEST_URL2 = "http://www.anguscardiacgroup.co.uk/Programme.htm"
TEST_URL2_RESULT = 20

class PlacemakerTest(TestCase):
	def test_url(self):
		"""
		Tests that 3 places are found in page at TEST_URL.
		"""
		g = geomaker(TEST_URL)
		p = g.find_places()
		# print 'testing geomaker...'
		# if p.places:
		#	  print	 p.geographic_scope
		#	  print	 p.administrative_scope
		#	  for place in p.places:
		#		  print '%s: %s, %s/%s - %s (%s)' % (place.placetype, place.name, place.centroid.latitude, place.centroid.longitude, place.woeid, place.confidence)
		# else:
		#	  print 'no places found'
		
		self.assertEqual(len(p.places), TEST_URL_RESULT)

class TermExtractorTest(TestCase):
	"""docstring for TermExtractorTest"""
	def test_url(self):
		terms = get_terms(TEST_URL2)
		print terms
		self.assertEqual(len(terms), TEST_URL2_RESULT)
		