# from django.db import models


from mongoengine import *
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
    
    # NB: latitude / longitude must be first 2 fields for mongo 2d index to work
    lat_lon = ListField(FloatField(), default=[])
    latitude = FloatField()
    longitude = FloatField()
    
    woeid = StringField()
    name = StringField()
    placetype = StringField()
        
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
    tags = ListField(StringField(max_length=96))
    collection_status = StringField()
    locations = ListField(ReferenceField(Location), default=[])
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


from mongoengine.connection import _get_db as get_db

def load_item_data(document, item_data):
    new_data = eval(item_data.read())
    db = get_db()
    db[document].insert(new_data)
    return db