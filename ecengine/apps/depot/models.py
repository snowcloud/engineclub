# from django.db import models


from mongoengine import *
from datetime import datetime

COLL_STATUS_NEW = 'new'
COLL_STATUS_LOC_CONF = 'location_confirm'
COLL_STATUS_ = ''
COLL_STATUS_ = ''
COLL_STATUS_COMPLETE = 'complete'
# COLLECTION_STATUS = ('new', )

class Location(EmbeddedDocument):
    """docstring for Place"""
    woeid = StringField()
    name = StringField()
    placetype = StringField()
    latitude = StringField()
    longitude = StringField()
        
# from placemaker.placemaker import Place

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
    loc_values = { 
        'woeid': values[0],
        'name': values[1],
        'placetype': values[2],
        'latitude': values[3],
        'longitude': values[4]
        }
    return Location(**loc_values)

class Item(Document):
    url = StringField(unique=True, required=True)
    title = StringField(required=True)
    description = StringField()
    postcode = StringField()
    area = StringField()
    tags = StringField()
    last_modified = DateTimeField(default=datetime.now)
    shelflife = StringField()
    author = StringField()
    status = StringField()
    collection_status = StringField()
    admin_note = StringField()
    locations = ListField(EmbeddedDocumentField(Location), default=[])

    def save(self, *args, **kwargs):
        created = (self.id is None) and not self.url.startswith('http://test.example.com')
        super(Item, self).save(*args, **kwargs)
        if created:
            print 'i am new- email me'


try:
    import simplejson as json
except:
    from django.utils import simplejson as json

from ecutils.utils import dict_to_string_keys

def load_item_data(item_data):
    items = json.load(item_data)
    for item in items:
        # can't pass in item dict as kwargs cos won't take unicode keys
        Item.objects.get_or_create(**dict_to_string_keys(item))
