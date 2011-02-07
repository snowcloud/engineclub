# Create your views here.
from django.conf import settings
import urllib
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler # import responses
from BeautifulSoup import BeautifulSoup
from firebox.yahoo_term_extractor import termextractor
from firebox.yahoo_place_types import PLACE_TYPES

# probably move this code to utils.py if enough
def get_url_content(url):
    """takes a url and returns the text content of the page"""
    try:
        response = urllib2.urlopen(url)
        htmltext = response.read()
    except urllib2.HTTPError, e:
        raise Exception(BaseHTTPRequestHandler.responses[e.code])
    
    soup = BeautifulSoup(htmltext)
    result = ''.join([e for e in soup.recursiveChildGenerator() if isinstance(e,unicode)])
    return result.encode('ascii', 'ignore')

from placemaker import placemaker

class geomaker(object):
    """docstring for geomaker"""
    def __init__(self, content):
        self.content = content
    
    def find_places(self):
        """docstring for places"""
        if self.content.startswith('http'):
            data = get_url_content(self.content)
        else:
            data = self.content
        p = placemaker(settings.YAHOO_KEY)
        p.find_places(data)
        return p

class PointProxy(object):
    """proxy object for a placemaker.Point"""
    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon
    
class PlaceProxy(object):
    """proxy object for a placemaker.PlacemakerPoint"""
    def __init__(self, loc, checked=False):
        super(PlaceProxy, self).__init__()
        self.woeid = loc.woeid
        self.name = loc.name
        self.placetype = loc.placetype
        self.centroid = PointProxy(loc.latitude, loc.longitude) 
        self.checked = checked

def get_terms(content):
    """docstring for termextractor"""
    if content.startswith('http'):
        data = get_url_content(content)
    else:
        data = content

    t = termextractor(settings.YAHOO_KEY)
    return t.extract_terms(data)

