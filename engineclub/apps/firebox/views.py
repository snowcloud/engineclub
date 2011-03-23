# Create your views here.
from django.conf import settings
import urllib
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler # import responses
from BeautifulSoup import BeautifulSoup
from firebox.yahoo_term_extractor import termextractor
from firebox.yahoo_place_types import PLACE_TYPES

from mongoengine import connect
from mongoengine.connection import _get_db as get_db

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
        data = content.encode('UTF8')

    t = termextractor(settings.YAHOO_KEY)
    return t.extract_terms(data)

from pymongo import Connection
import codecs
import csv

def load_postcodes(fname):
    """docstring for load_postcodes"""
    
    connection = Connection()
    db = connection[settings.MONGO_DB]
    postcode_coll = db.postcode_locations
    postcode_coll.drop()
    
    print 'postcode collection (start): ', postcode_coll.count()
    
    f = codecs.open(fname, 'rt')
    try:
        reader = csv.reader(f, delimiter='\t',)
        for r in reader:
            # print r[1].replace(' ', ''), r[9], r[10]
            try:
                postcode_coll.insert({'postcode': r[1].replace(' ', ''), 'latlon': [float(r[9]), float(r[10])]})
            except ValueError:
                print r
    finally:
        f.close()
    print 'postcode collection (end):', postcode_coll.count()
    print postcode_coll.find_one({'postcode': 'AB565UB'})
    print postcode_coll.find_one({'postcode': 'AB101AX'})

def load_placenames(fname):
    """docstring for load_postcodes
    geonameid	name	asciiname	alternatenames	latitude	longitude	feature class	feature code	country code	cc2	admin1 code	admin2 code	admin3 code	admin4 code	population	elevation	gtopo30	timezone	modification date
    2633415	Yarm	Yarm	Yarm,Yarm on Tees	54.50364	-1.35793	P	PPL	GB		ENG	J7			0		31	Europe/London	9 Dec 2010
    
    """
    
    connection = Connection()
    db = connection[settings.MONGO_DB]
    placename_coll = db.placename_locations
    placename_coll.drop()
    
    print 'placename collection (start): ', placename_coll.count()
    
    f = codecs.open(fname, 'rt')
    try:
        reader = csv.reader(f, delimiter='\t',)
        for r in reader:
            # ONLY LOADING SCOTLAND
            if r[10] == 'SCT':
                # print r[1], r[4], r[5]
                try:
                    placename_coll.insert({
                        'name': r[1],
                        'name_upper': r[1].upper(),
                        'latlon': [float(r[4]), float(r[5])]})
                except ValueError:
                    print r
    finally:
        f.close()
    print 'placename collection (end):', placename_coll.count()
    print placename_coll.find_one({'name_upper': 'KEITH'})
    print placename_coll.find_one({'name_upper': 'PORTOBELLO'})


