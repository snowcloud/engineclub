# Create your views here.
import codecs
import csv
import time
import urllib
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler # import responses
from BeautifulSoup import BeautifulSoup
# from firebox.yahoo_term_extractor import termextractor
# from firebox.yahoo_place_types import PLACE_TYPES

from django.conf import settings
from mongoengine import connect
from mongoengine.connection import _get_db as get_db
from pysolr import Solr
from pymongo import Connection, DESCENDING, ASCENDING, GEO2D
from bson.dbref import DBRef

from depot.models import Resource, Location, lookup_postcode, \
    POSTCODE, POSTCODEDISTRICT, OSM_PLACENAME


import logging
logger = logging.getLogger('aliss')

def load_locations(path, dbname):

    print '... from %s:%s' % (dbname, path)
    connection = Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
    db = connection[dbname]

    # test_google()
    # test_unlock()

    # print lookup_postcode('227-229 Niddrie Mains Road')
    # print lookup_postcode('AB10')


    # coll = db.location
    # print 'location:', coll.find_one({'os_id': 'AB101SB'})

    # print

    # coll = db.newlocation
    # loc = coll.find_one({'_id': 'AB101SB'})
    # print 'newlocation:', loc

    # print

    # coll = db.newlocation
    # loc = coll.find_one({'_id': 'AB10'})
    # print 'newlocation:', loc

    # print

    # loc = coll.find_one({'_id': 'EH152QR'})
    # print 'newlocation:', loc


    # return



    coll = db.location

    coll.drop()

    # load_os_gb(path, coll)
    load_os_gb_full(path, coll, sct=True)
    load_osm_places(path, coll)
    add_missing_districts(coll)

    make_corrections(coll)

    # move_to_newlocation(db)

    # update_location_collection(coll)

    recreate_indexes(coll)
    print 'wee test...'
    print coll.find_one({'place_name': 'Pollok', 'country_code': 'SCT'})

def bak_locations(dbname):
    print 'backing up location ids to tmp_locations using %s' % settings.MONGO_DATABASE_NAME
    print 'Locations (before):', Location.objects.count()
    # DO THIS FIRST TO GET LOC IDS

    # for res in Resource.objects[2000:2200]:
    for res in Resource.objects:
        res.tmp_locations = [loc.label for loc in res.locations]
        # print res.tmp_locations
        res.save()
        # print res.id, res.locations, res.tmp_locations
    Location.drop_collection()
    print 'Locations (after):', Location.objects.count()

def convert_to_newlocations(dbname):

    def _get_loc(pc, coll):
        _new_loc = None
        _loc = coll.find_one({'postal code': pc})
        if _loc:
            district = ', %s' % _loc['admin name3'] if _loc['admin name3'] else ''
            place_name = '%s%s' % ((_loc['place name'], district))
            place_name = place_name.replace(' Ward', '') #.replace(' City', '')
            loc_type = POSTCODE if len(pc) > 4 else POSTCODEDISTRICT

            _new_loc = Location(
                id= _loc['postal code'].replace(' ', ''),
                postcode= _loc['postal code'],
                place_name= place_name,
                lat_lon= [float(_loc['latitude']), float(_loc['longitude'])],
                loc_type= loc_type,
                accuracy= _loc['accuracy'],
                district= _loc['admin name3'],
                country_code= _loc['admin code1'])
            _new_loc.save()

        print _new_loc, _new_loc.loc_type
        return _new_loc

    print 'convert_to_newlocations using %s' % settings.MONGO_DATABASE_NAME

    connect(dbname, host=settings.MONGO_HOST, port=settings.MONGO_PORT)

    connection = Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
    db = connection[dbname]
    coll = db.fullpc

    print 'Resources:', Resource.objects.count()
    print 'Locations:', Location.objects.count()
    # print 'NewLocations:', NewLocation.objects.count()
    
    for res in Resource.objects:

        locs = []
        # print res.tmp_locations
        for loc_id in res.tmp_locations:
            try:
                loc = Location.objects.get(postcode=loc_id)
                # print loc
            except Location.DoesNotExist, e:
                print '*** not found:', loc_id #, loc.label, res.title, res.id
                loc = _get_loc(loc_id, coll)
            locs.append(loc)
        res.locations = locs
        res.save()

def fix_pcdistricts(dbname):
    """
    Postcode districts, eg PA1, don't have good lat/lons cos geonames file has multiple entries.
    Use google lookup to sort them.
    """

    count = Location.objects(loc_type="POSTCODEDISTRICT").count()
    print 'location:', count

    for i in range(0, count, 5):

        print i, i+5
        for pcdistrict in Location.objects(loc_type="POSTCODEDISTRICT")[i:i+5]:
            res, addr = lookup_postcode(pcdistrict.postcode)
            pcdistrict.lat_lon = (res.geometry.location.lat, res.geometry.location.lng)
            print pcdistrict.lat_lon
            pcdistrict.save()
        # needs a delay or google complains
        time.sleep(5) # seconds



# def test_google():

#     """
# v2 with key
# http://maps.google.com/maps/geo?key=<key>&output=xml&q=Abernethy
# out=csv
# 200,4,56.3320140,-3.3137140

# see below:


# lat,lon to pc
# (55.9453585, -3.1018994)
# {u'country': u'GB', u'postal_code': u'EH15 2QR', u'administrative_area_level_2': u'City of Edinburgh', u'locality': u'Edinburgh'}

#     """

#     from googlegeocoder import GoogleGeocoder
#     geocoder = GoogleGeocoder()

#     print '\npostcode to lat,lon'
#     search = geocoder.get('PO19', region='UK')
#     res, addr = _make_addr(search)
#     print '\npostcode to lat,lon'
#     search = geocoder.get('PO123BY', region='UK')
#     res, addr = _make_addr(search)


#     print '\nplace to lat_lon'    
#     search = geocoder.get("Chichester", region='UK')
#     res, addr = _make_addr(search)
    

#     print '\nreverse lat_lon to address'
#     search = geocoder.get((search[0].geometry.location.lat, search[0].geometry.location.lng))
#     res, addr = _make_addr(search)

#     print '\nlat_lon to address'
#     print 'Pollok (from osm)'
#     Pollok = (55.827068699999998, -4.3456574999999997)
#     search = geocoder.get(Pollok)
#     res, addr = _make_addr(search)

#     Gosport = (50.802154926519805, -1.1592288410260432)
#     search = geocoder.get(Gosport)
#     res, addr = _make_addr(search)

# def test_unlock():

#     """
#     looks like Unlock is more accurate using 'os' gazetteer, but that needs an api key.

#     or just use http://unlock.edina.ac.uk/ws/search?format=json&count=no&name=Pollok, GB

#     format: 'json', // Retrieve the results in JSON format
#     maxRows: 10, // Limit the number of results to 10
#     count: 'no', // Prevent Unlock from counting the total possible results (faster)
#     name:

#     Gosport PO12 3BY
#     """

#     from unlock import Places
#     import requests

#     def _postCodeSearch(place,postCode=None,format='txt'):
#         """postCodeSearch?postCode=EH91PR&gazetteer=unlock&format=txt"""

#         params = {'postCode':postCode,'format':format, 'gazetteer':place.pick_gazetteer()}   
#         results = place.ask_service('postCodeSearch',params)
#         return results

#     p = Places()

#     # xml = p.nameSearch('Pollok, GB')
#     # print xml

#     # r = requests.get('http://unlock.edina.ac.uk/ws/search?format=json&maxRows=50&count=no&name=Pollok,%20GB')
#     # print r.status_code
#     # print r.content

#     txt = _postCodeSearch(p, 'PO123BY')
#     print txt


def recreate_indexes(coll):
    print 'recreated indexes...'
    coll.drop_indexes()
    coll.ensure_index([
        ('place_name', ASCENDING),
        ('country_code', ASCENDING),
        ('accuracy', DESCENDING)
        ])
    coll.ensure_index([('lat_lon', GEO2D)])

def load_os_gb(path, coll):
    """docstring for load_postcodes

    from readme.txt
    ===============
    0 country code      : iso country code, 2 characters
    1 postal code       : varchar(20)
    2 place name        : varchar(180)
    3 admin name1       : 1. order subdivision (state) varchar(100)
    4 admin code1       : 1. order subdivision (state) varchar(20)
    5 admin name2       : 2. order subdivision (county/province) varchar(100)
    6 admin code2       : 2. order subdivision (county/province) varchar(20)
    7 admin name3       : 3. order subdivision (community) varchar(100)
    8 admin code3       : 3. order subdivision (community) varchar(20)
    9 latitude          : estimated latitude (wgs84)
    10 longitude         : estimated longitude (wgs84)
    11 accuracy          : accuracy of lat/lng from 1=estimated to 6=centroid
    
    GB  AB10    Aberdeen    Scotland    SCT Aberdeenshire               57.1193 -2.3194 1

    probs:
        * placenames missing, small num at end - discarding
        * lat/lons missing, small num at end - discarding
        * country codes missing/wrong - including, could fix using district?
        * accuracy < 4 is useless- most are well off, so discarding

    """
    
    fname = 'geonames/GB-postcodes/GB.txt'
    print 'loading os gb short codes'
    print 'collection (start): ', coll.count()
    
    f = codecs.open('%s/%s' % (path, fname), 'rt')
    try:
        reader = csv.reader(f, delimiter='\t',)
        for r in reader:
            # print r[1].replace(' ', ''), r[9], r[10]
            try:
                accuracy = int(r[11])
                # remove 'Ward' from place_name and add r[7] with City removed if nec
                if r[2] and (r[9] or r[10]) and accuracy > 3: # or r[7]:
                    # place_name = ', '.join((r[2], r[7]))
                    # place_name = place_name.replace(' Ward', '').replace(' City', '')
                    # print r[1], '|', r[2], '|', r[9], r[10]
                    coll.insert(
                        {   '_id': r[1].replace(' ', ''),
                            'postcode': r[1],
                            'place_name': r[2],
                            'lat_lon': [float(r[9]), float(r[10])],
                            'loc_type': POSTCODEDISTRICT,
                            'accuracy': r[11],
                            'district': r[5],
                            'country_code': r[4],
                        }
                    )
                else:
                    pass
                    # place_name = ''
                    # print r
            except ValueError:
                print 'discarding', r
    finally:
        f.close()

    print 'collection (end):', coll.count()


def load_os_gb_full(path, coll, sct=False):
    """docstring for load_os_full

    from readme.txt
    ===============
    0 country code      : iso country code, 2 characters
    1 postal code       : varchar(20)
    2 place name        : varchar(180)
    3 admin name1       : 1. order subdivision (state) varchar(100)
    4 admin code1       : 1. order subdivision (state) varchar(20)
    5 admin name2       : 2. order subdivision (county/province) varchar(100)
    6 admin code2       : 2. order subdivision (county/province) varchar(20)
    7 admin name3       : 3. order subdivision (community) varchar(100)
    8 admin code3       : 3. order subdivision (community) varchar(20)
    9 latitude          : estimated latitude (wgs84)
    10 longitude         : estimated longitude (wgs84)
    11 accuracy          : accuracy of lat/lng from 1=estimated to 6=centroid
    
    ['GB', 'AB10 1AA', 'George St/Harbour Ward', 'Scotland', 'SCT', '', '00', 
    'Aberdeen City', 'QA', '57.1482338750867', '-2.09664792921131', '6']
    probs:
        * 

    """
    
    # fname = 'geonames/GB-postcodes/GB_full_AB.csv'
    fname = 'geonames/GB-postcodes/GB_full.csv'
    print 'loading os gb full postcodes'
    print 'collection (start): ', coll.count()
    
    f = codecs.open('%s/%s' % (path, fname), 'rt')
    try:
        reader = csv.reader(f, delimiter='\t',)
        for r in reader:
            # print r[1].replace(' ', ''), r[9], r[10]
            try:
                # remove 'Ward' from place_name and add r[7] with City removed if nec
                if (not sct or r[4] == 'SCT') and r[2] and (r[9] or r[10]):
                    place_name = ', '.join((r[2], r[7]))
                    place_name = place_name.replace(' Ward', '') #.replace(' City', '')
                    # print r[1], '|', r[2], '|', r[9], r[10]
                    coll.insert(
                        {   '_id': r[1].replace(' ', ''),
                            'postcode': r[1],
                            'place_name': place_name,
                            'lat_lon': [float(r[9]), float(r[10])],
                            'loc_type': POSTCODE,
                            'accuracy': r[11],
                            'district': r[7],
                            'country_code': r[4],
                        }
                    )
                else:
                    if not sct:
                        print r
                # if r[1] == 'AB10 1AA':
                #     print r
            except ValueError:
                print r
    finally:
        f.close()

    print 'collection (end):', coll.count()

class FoundPlace(object):
    """docstring for FoundPlace"""
    tags = {}
    def __init__(self, id, lat, lon):
        self.id, self.lat, self.lon = id, lat, lon
        self.tags = {}

    def __str__(self):
        return '%s %s %s (%s)' % (self.lat, self.lon, self.name, self.tags.get('place', '-no place-'))
    def __unicode__(self):
        return u'%s %s %s (%s)' % (self.lat, self.lon, self.name.decode('utf-8'), self.tags.get('place', u'-no place-'))
    def _name(self):
        return self.tags.get('name:en', u'') or self.tags.get('name', u'')
    name = property(_name)

class ParserTarget:
    places = []
    current_node = None
    def start(self, tag, attrib):
        if tag == 'node':
            self.current_node = FoundPlace(attrib['id'], attrib['lat'], attrib['lon'])
        elif tag == 'tag':
            self.current_node.tags[attrib['k']] = unicode(attrib['v']).encode('utf-8')
    def end(self, tag):
        if tag == 'node' and (self.current_node.tags.get('place') in ['suburb', 'village', 'hamlet', 'locality', 'town', 'city']):
            if self.current_node.name == '':
                print 'discarding %s - no name in %s' % (self.current_node.id, self.current_node.tags)
            else:
                self.places.append(self.current_node)
            # self.current_node = None

    def close(self):
        places, self.places = self.places, []
        # print 'close'
        return places


def load_osm_places(path, coll):
    """

    suburb, village, town
    """
    from lxml import etree

    fname = 'openstreetmap/scotland.osm'
    # fname = 'openstreetmap/scotland-test.osm'
    # outname = 'openstreetmap/scotland-out.csv'

    parser_target = ParserTarget()
    parser = etree.XMLParser(target=parser_target)

    print 'loading osm places in scotland'
    print 'collection (start): ', coll.count()
    
    places = etree.parse('%s/%s' % (path, fname), parser)

    # print(parser_target.close_count)

    for place in places:
        coll.insert(
            {   '_id': place.id,
                #'postcode': r[1],
                'place_name': place.name,
                'lat_lon': [float(place.lat), float(place.lon)],
                'loc_type': OSM_PLACENAME,
                'accuracy': '6',
                # 'district': ,
                'country_code': 'SCT',
            }
        )

    print 'collection (end):', coll.count()


def add_missing_districts(coll):
    print 'adding missing districts...'
    print 'to %s locations' % coll.find({ 'district': { '$exists' : False } }).count()

    print 'ensuring index...'
    coll.ensure_index([('lat_lon', GEO2D)])

    for loc in coll.find({ 'district': { '$exists' : False } }):
        d = coll.find_one({ 'district': { '$exists' : True }, 'lat_lon': { '$near': loc['lat_lon']} })
        # print '-', loc['_id'], loc.get('district', '.'), 'from', d['_id'], d['district']
        coll.update({"_id": loc['_id']}, {"$set": {"district": d['district']}})

    print 'now %s locations with no district' % coll.find({ 'district': { '$exists' : False } }).count()

    # for loc in NewLocation.objects(district__exists=False):
    #     # print loc.place_name, loc.district, loc.lat_lon
    #     d = NewLocation.objects(district__exists=True, lat_lon__near=loc.lat_lon)[0]
    #     loc.district = d.district
    #     loc.save()
    #     # print '- ', d.district

def make_corrections(coll):

    keys = [
        {'place_name':'Abernethy', 'district':"Perth and Kinross", 'lat_lon':[56.3324076, -3.3193698]},
        {'place_name':'Achiemore', 'district':"Highland", 'lat_lon':[58.5683787, -4.8202016]},
        {'place_name':'Achintee', 'district':"Highland", 'lat_lon':[57.4187707, -5.428257]},
        {'place_name':'Aird', 'district':"Na H-Eileanan an Iar", 'lat_lon':[58.2471053, -6.3314044]},
        # {'place_name':'', 'district':"", 'lat_lon':[]},
        # {'place_name':'', 'district':"", 'lat_lon':[]},
        # {'place_name':'', 'district':"", 'lat_lon':[]},
        # {'place_name':'', 'district':"", 'lat_lon':[]},
        ]
    for key in keys:
        coll.remove(key)
    
# def move_to_newlocation(db):
#     print 'move_to_newlocation using %s' % settings.MONGO_DATABASE_NAME
    
#     print 'doing %s resources' % db.resource.count()

#     for res in db.resource.find():
#         locs = [db.dereference(loc) for loc in res.get('locations', [])]

#         if locs:
#             newlocs = [DBRef('newlocation', loc['os_id']) for loc in locs]
#             db.resource.update({"_id": res['_id']}, {"$set": {"locations": newlocs}})




def reindex_resources(dbname, url=settings.SOLR_URL, printit=False):
    """docstring for reindex_resources"""
    # logger.error("indexing resources:")

    from depot.models import Resource

    if printit:
        print 'CLEARING SOLR INDEX: ', url
    conn = Solr(url)
    conn.delete(q='*:*')
    batch_size = getattr(settings, 'SOLR_BATCH_SIZE', 100)
    if printit:
        print 'Indexing %s Resources... (batch: %s)' % (Resource.objects.count(), batch_size)
    
    docs = []
    for i, res in enumerate(Resource.objects):
        docs.extend(res.index())
        if i % batch_size == 0:
            conn.add(docs)
            docs = []
    conn.add(docs)

###############################################################

# OLD CODE- NEEDS CHECKED IF ANYTHING STILL USED, OTHERWISE DELETE

# # probably move this code to utils.py if enough
# def get_url_content(url):
#     """takes a url and returns the text content of the page"""
#     try:
#         response = urllib2.urlopen(url)
#         htmltext = response.read()
#     except urllib2.HTTPError, e:
#         raise Exception(BaseHTTPRequestHandler.responses[e.code])
    
#     soup = BeautifulSoup(htmltext)
#     result = ''.join([e for e in soup.recursiveChildGenerator() if isinstance(e,unicode)])
#     return result.encode('ascii', 'ignore')

# from placemaker import placemaker

# class geomaker(object):
#     """docstring for geomaker"""
#     def __init__(self, content):
#         self.content = content
    
#     def find_places(self):
#         """docstring for places"""
#         if self.content.startswith('http'):
#             data = get_url_content(self.content)
#         else:
#             data = self.content
#         p = placemaker(settings.YAHOO_KEY)
#         p.find_places(data)
#         return p

# class PointProxy(object):
#     """proxy object for a placemaker.Point"""
#     def __init__(self, lat, lon):
#         self.latitude = lat
#         self.longitude = lon
    
# class PlaceProxy(object):
#     """proxy object for a placemaker.PlacemakerPoint"""
#     def __init__(self, loc, checked=False):
#         super(PlaceProxy, self).__init__()
#         self.woeid = loc.woeid
#         self.name = loc.name
#         self.placetype = loc.placetype
#         self.centroid = PointProxy(loc.latitude, loc.longitude) 
#         self.checked = checked

# def get_terms(content):
#     """docstring for termextractor"""
#     if content.startswith('http'):
#         data = get_url_content(content)
#     else:
#         data = content.encode('UTF8')

#     t = termextractor(settings.YAHOO_KEY)
#     return t.extract_terms(data)


# def load_postcodes(fname, dbname):
#     """docstring for load_postcodes
    
#     from readme.txt
#     ===============
#     country code      : iso country code, 2 characters
#     postal code       : varchar(10)
#     place name        : varchar(180)
#     admin name1       : 1. order subdivision (state) varchar(100)
#     admin code1       : 1. order subdivision (state) varchar(20)
#     admin name2       : 2. order subdivision (county/province) varchar(100)
#     admin code2       : 2. order subdivision (county/province) varchar(20)
#     admin name3       : 3. order subdivision (community) varchar(100)
#     admin code3       : 3. order subdivision (community) varchar(20)
#     latitude          : estimated latitude (wgs84)
#     longitude         : estimated longitude (wgs84)
#     accuracy          : accuracy of lat/lng from 1=estimated to 6=centroid
    
#     GB	AB10	Midstocket/Rosemount Ward	Scotland	SCT		00	Aberdeen City	QA	57.1454241278722	-2.10952454025988	6
#     """
    
#     connection = Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
#     db = connection[dbname]
#     postcode_coll = db.postcode_locations
#     postcode_coll.drop()
    
#     print 'postcode collection (start): ', postcode_coll.count()
    
#     f = codecs.open(fname, 'rt')
#     try:
#         reader = csv.reader(f, delimiter='\t',)
#         for r in reader:
#             # print r[1].replace(' ', ''), r[9], r[10]
#             try:
#                 # remove 'Ward' from place_name and add r[7] with City removed if nec
#                 place_name = '%s, %s' % (r[2], r[7])
#                 place_name = place_name.replace(' Ward', '').replace(' City', '')
#                 # print place_name
#                 postcode_coll.insert({'postcode': r[1].replace(' ', ''), 'label': r[1], 'place_name': place_name, 'lat_lon': [float(r[9]), float(r[10])]})
#             except ValueError:
#                 print r
#     finally:
#         f.close()
        
#     # for loc in Location.objects[:10]:
#     #     # loc.place_name = postcode_coll.find_one({'postcode': loc.os_id})['place_name']
#     #     loc.save()
        
#     print 'postcode collection (end):', postcode_coll.count()
#     print postcode_coll.find_one({'postcode': 'AB565UB'})
#     print postcode_coll.find_one({'postcode': 'AB101AX'})
    

# def load_placenames(fname, dbname):
#     """docstring for load_postcodes
#     geonameid	name	asciiname	alternatenames	latitude	longitude	feature class	feature code	country code	cc2	admin1 code	admin2 code	admin3 code	admin4 code	population	elevation	gtopo30	timezone	modification date
#     2633415	Yarm	Yarm	Yarm,Yarm on Tees	54.50364	-1.35793	P	PPL	GB		ENG	J7			0		31	Europe/London	9 Dec 2010
    
#     """
#     connection = Connection(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
#     db = connection[dbname]
#     placename_coll = db.placename_locations
#     placename_coll.drop()
    
#     print 'placename collection (start): ', placename_coll.count()
    
#     f = codecs.open(fname, 'rt')
#     try:
#         reader = csv.reader(f, delimiter='\t',)
#         for r in reader:
#             # ONLY LOADING SCOTLAND
#             if r[10] == 'SCT':
#                 # print r[1], r[4], r[5]
#                 try:
#                     placename_coll.insert({
#                         'name': r[1],
#                         'name_upper': r[1].upper(),
#                         'lat_lon': [float(r[4]), float(r[5])]})
#                 except ValueError:
#                     print r
#     finally:
#         f.close()
#     print 'placename collection (end):', placename_coll.count()
#     print placename_coll.find_one({'name_upper': 'KEITH'})
#     print placename_coll.find_one({'name_upper': 'PORTOBELLO'})

