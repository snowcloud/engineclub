# from django.db import models

from django.conf import settings

from mongoengine import *
from mongoengine.connection import _get_db as get_db
from datetime import datetime
    
from pymongo import Connection, GEO2D
from pysolr import Solr

from engine_groups.models import Account

COLL_STATUS_NEW = 'new'
COLL_STATUS_LOC_CONF = 'location_confirm'
COLL_STATUS_TAGS_CONF = 'tags_confirm'
COLL_STATUS_ = ''
COLL_STATUS_COMPLETE = 'complete'
        
class ItemMetadata(EmbeddedDocument):
    last_modified = DateTimeField(default=datetime.now)
    author = ReferenceField(Account)
    shelflife = DateTimeField(default=datetime.now) # TODO set to now + settings.DEFAULT_SHELFLIFE
    status = StringField()
    note = StringField()
            
class Location(Document):
    """Location document, based on Ordnance Survey data
    ALISS only uses 4 types: postcode, ward, district, country
    """    
    os_id = StringField(unique=True, required=True)
    label = StringField(required=True)
    place_name = StringField()
    os_type = StringField(required=True)
    parents = ListField(ReferenceField("Location"), default=list)
    lat_lon = GeoPointField()
    
class Moderation(EmbeddedDocument):
    outcome = StringField()
    note = StringField()
    owner = ReferenceField(Account)
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

class Curation(EmbeddedDocument):
    outcome = StringField()
    tags = ListField(StringField(max_length=96), default=list)
    # rating - not used
    note = StringField()
    data = DictField()
    owner = ReferenceField(Account)
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

def place_as_cb_value(place):
    """takes placemaker.Place and builds a string for use in forms (eg checkbox.value) to encode place data"""
    if place:
        return '%s|%s|%s|%s|%s' % (place.woeid,place.name,place.placetype,place.centroid.latitude,place.centroid.longitude)
    return ''

def location_from_cb_value(cb_value):
    """takes cb_string and returns Location"""
    values = cb_value.split('|')
    if not len(values) == 5:
        raise Exception('place_from_cb_value could not make a Location from values: %s' % values)
    lat = float(values[3])
    lon = float(values[4])
    print lat, lon
    loc_values = {
        'lat_lon': [lat, lon],
        # 'woeid': values[0],
        'name': values[1],
        'placetype': values[2],
        'latitude': lat,
        'longitude': lon
        }
    return Location.objects.get_or_create(woeid=values[0], defaults=loc_values)

class Resource(Document):
    """uri is now using ALISS ID. Could also put a flag in resources for canonical uri?"""
    # uri = StringField(unique=True, required=True)
    title = StringField(required=True)
    description = StringField()
    resource_type = StringField()
    uri = StringField()
    locations = ListField(ReferenceField(Location), default=list)
    service_area = ListField(ReferenceField(Location), default=list)
    moderations = ListField(EmbeddedDocumentField(Moderation), default=list)
    curations = ListField(EmbeddedDocumentField(Curation), default=list)
    tags = ListField(StringField(max_length=96), default=list)
    related_resources = ListField(ReferenceField('RelatedResource'))
    owner = ReferenceField(Account)
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

    def save(self, *args, **kwargs):
        self.item_metadata.last_modified = datetime.now()
        # print local_id
        # if self.owner:
        # self.item_metadata.author = Account.objects.get(local_id=local_id)
        # created = (self.id is None) # and not self.url.startswith('http://test.example.com')
        if self.id is None:
            if not self.moderations:
                obj = Moderation(outcome='OK', owner=self.owner)
                obj.item_metadata.author = self.owner
                self.moderations.append(obj)
            if not self.curations:
                obj = Curation(outcome='OK', tags=self.tags, owner=self.owner)
                obj.item_metadata.author = self.owner
                self.curations.append(obj)
        super(Resource, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """docstring for delete"""
        conn = Solr(settings.SOLR_URL)
        conn.delete(q='id:%s' % self.id)        
        super(Resource, self).delete(*args, **kwargs)
        
    def reindex(self):
        """docstring for reindex"""
        conn = Solr(settings.SOLR_URL)
        conn.delete(q='id:%s' % self.id)
        self.index(conn)
        
    def index(self, conn=None):
        """conn is Solr connection"""
        doc = {
            'id': unicode(self.id),
            'res_id': unicode(self.id),
            'title': self.title,
            'description': self.description,
            'keywords': ', '.join(self.tags)
        }
        if self.locations:
            doc['pt_location'] = lat_lon_to_str(self.locations[0])
        if conn:
            conn.add([doc])
        return doc

    def add_location_from_name(self, placestr):
        """place_str can be anything"""
        # first get a geonames postcode or place
        place = get_place_for_postcode(placestr) or get_place_for_placename(placestr)
        if place:
            # if it's a postcode already, fine, otherwise use the lat_lon to get a postcode
            postcode = place.get('postcode', None) or get_postcode_for_lat_lon(place['lat_lon'])['postcode']
            location, created = get_location_for_postcode(postcode)
            if location not in self.locations:
                self.locations.append(location)
                self.save()

class RelatedResource(Document):
    """docstring for RelatedResource"""
    source = ReferenceField(Resource)
    target = ReferenceField(Resource)
    rel_type = StringField()
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)    


def load_resource_data(document, resource_data):
    new_data = eval(resource_data.read())
    db = get_db()
    db[document].insert(new_data)
    return db

def _get_or_create_location(result):
    """return Location, created (bool) if successful"""
    if result:
        loc_values = {
            'label': result['label'],
            'place_name': result['place_name'],
            'os_type': 'POSTCODE',
            'lat_lon': result['lat_lon'],
            }
        return Location.objects.get_or_create(os_id=result['postcode'], defaults=loc_values)
    raise Location.DoesNotExist
    
def get_location_for_postcode(postcode):
    result = get_place_for_name(postcode, 'postcode_locations', 'postcode', settings.MONGO_DB)
    if not result and len(postcode.split()) > 1:
        print 'trying ', postcode.split()[0]
        result = get_place_for_name(postcode.split()[0], 'postcode_locations', 'postcode', settings.MONGO_DB)
    return _get_or_create_location(result)

def get_place_for_name(namestr, collname, field, dbname):
    """return place from geonames data- either postcode or named place depending on collname
    
    {u'label': u'EH15 2QR', u'_id': ObjectId('4d91fd593de0748efd0734b4'), u'postcode': u'EH152QR', u'lat_lon': [55.945360336317798, -3.1018998114292899], u'place_name': u'Portobello/Craigmillar Ward'}
    {u'name_upper': u'KEITH', u'_id': ObjectId('4d8e0a013de074fdef000fad'), u'name': u'Keith', u'lat_lon': [57.53633, -2.9481099999999998]}
    
    """
    name = namestr.upper().replace(' ', '').strip()
    connection = Connection()
    db = connection[dbname]
    coll = db[collname]
    result = coll.find_one({field: name})
    if result:
        return result
    return None

def get_place_for_postcode(name, dbname=settings.MONGO_DB):
    return get_place_for_name(name, 'postcode_locations', 'postcode', dbname)
    
def get_place_for_placename(name, dbname=settings.MONGO_DB):
    return get_place_for_name(name, 'placename_locations','name_upper',  dbname)

def get_postcode_for_lat_lon(lat_lon, dbname=settings.MONGO_DB):
    """looks up nearest postcode for lat_lon in geonames data"""
    connection = Connection()
    db = connection[dbname]
    coll = db['postcode_locations']
    coll.create_index([("lat_lon", GEO2D)])
    result = coll.find_one({"lat_lon": {"$near": lat_lon}})
    if result:
        return result
    return None

def lat_lon_to_str(loc):
    """docstring for lat_lon_to_str"""
    if loc:
        if type(loc) == Location:
            return (settings.LATLON_SEP).join([unicode(loc.lat_lon[0]), unicode(loc.lat_lon[1])])
        return (settings.LATLON_SEP).join([unicode(loc[0]), unicode(loc[1])])
    else:
        return ''

def find_by_place(name, kwords):
    conn = Solr(settings.SOLR_URL)
    loc = get_place_for_postcode(name) or get_place_for_placename(name)
    if loc:
        kw = {
            'rows': settings.SOLR_ROWS,
            'fl': '*,score',
            'qt': 'resources',
            'sfield': 'pt_location',
            'pt': lat_lon_to_str(loc['lat_lon']),
            'bf': 'recip(geodist(),2,200,20)^3',
            'sort': 'score desc',
        }
        return loc['lat_lon'], conn.search(kwords.strip() or '*:*', **kw)
    else:
        return None, None

def find_by_place_or_kwords(name, kwords):
    """docstring for find_by_place_or_kwords"""
    conn = Solr(settings.SOLR_URL)
    if name:
        return find_by_place(name, kwords)
    # keywords only
    kw = {
        'rows': settings.SOLR_ROWS,
        'fl': '*,score',
        'qt': 'resources',
    }
    return None, conn.search(kwords.strip() or '*:*', **kw)

