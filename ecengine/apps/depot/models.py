# from django.db import models


from mongoengine import *
from mongoengine.connection import _get_db as get_db
from datetime import datetime

COLL_STATUS_NEW = 'new'
COLL_STATUS_LOC_CONF = 'location_confirm'
COLL_STATUS_TAGS_CONF = 'tags_confirm'
COLL_STATUS_ = ''
COLL_STATUS_COMPLETE = 'complete'
# COLLECTION_STATUS = ('new', )

class ItemMetadata(EmbeddedDocument):
    last_modified = DateTimeField(default=datetime.now)
    shelflife = DateTimeField(default=datetime.now) # TODO set to now + settings.DEFAULT_SHELFLIFE
    author = StringField()
    status = StringField()
    admin_note = StringField()
    
class Location(Document):
    """Location document, based on Yahoo Placemaker data"""
    
    lat_lon = ListField(FloatField(), default=[])
    latitude = FloatField()
    longitude = FloatField()
    
    woeid = StringField()
    name = StringField()
    placetype = StringField()
    
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

class Item(Document):
    url = StringField(unique=True, required=True)
    title = StringField(required=True)
    description = StringField()
    postcode = StringField()
    area = StringField()
    locations = ListField(StringField(), default=[])
    tags = ListField(StringField(max_length=96))
    collection_status = StringField()
    metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

    # def __init__(self, *args, **kwargs):
    #     super(Item, self).__init__(*args, **kwargs)
    #     print 'item __init__'
        
    def save(self, author=None, *args, **kwargs):
        self.metadata.last_modified = datetime.now()
        if author:
            self.metadata.author = author
        created = (self.id is None) and not self.url.startswith('http://test.example.com')
        super(Item, self).save(*args, **kwargs)
        if created:
            # TODO
            print 'i am new- email me'

    def get_locations(self):
        return [Location.objects.get(woeid=id) for id in self.locations]

def get_nearest(lat, lon, categories=[], num=10, all_locations=False):
    """uses mongodb geo index to find num nearest locations to lat, lon parameters.
        returns list of dicts, each dict has:
        - dist (distance from lat,lon in degrees)
        - obj (dict of place attrs)
        - items (list of items in db at that location)"""
       
    db = get_db()
    db.eval('db.location.ensureIndex( { lat_lon : "2d" } )')
    eval_result = db.eval('db.runCommand( { geoNear : "location" , near : [%s,%s], num : %s } );' % (lat, lon, num))
    results = eval_result['results']
    for res in results:
        res['dis'] = res['dis'] * 111.12 # convert to Km
        if len(categories) > 0:
            print 'using cats ', len(categories)
            res['items'] = list(Item.objects(locations__in=[res['obj']['woeid']],tags__in=categories))
        else:
            res['items'] = list(Item.objects(locations__in=[res['obj']['woeid']]))
        print 'cats: ', categories
        print 'items: ', res['items'] 
    return [res for res in results if res['items']]


def load_item_data(document, item_data):
    new_data = eval(item_data.read())
    db = get_db()
    db[document].insert(new_data)
    return db