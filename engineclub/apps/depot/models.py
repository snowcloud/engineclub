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

# class Keyword(Document):
#   """docstring for Keyword"""
#   value = IntegerField()
        
class ItemMetadata(EmbeddedDocument):
    last_modified = DateTimeField(default=datetime.now)
    author = StringField()
    shelflife = DateTimeField(default=datetime.now) # TODO set to now + settings.DEFAULT_SHELFLIFE
    status = StringField()
    note = StringField()
            
class Location(Document):
    """Location document, based on Yahoo Placemaker woeid, + placeholders for move to Ordnance Survey data"""
    
    woeid = StringField()
    name = StringField()
    placetype = StringField()
    postcode = StringField()
    lat_lon = ListField(FloatField())
    latitude = FloatField()
    longitude = FloatField()
    os_id = StringField()
    os_placetype = StringField()

class Moderation(EmbeddedDocument):
    outcome = StringField()
    note = StringField()
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

class Curation(EmbeddedDocument):
    outcome = StringField()
    tags = ListField(StringField(max_length=96), default=list)
    # rating - not used
    note = StringField()
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

class AddedMetadata(EmbeddedDocument):
    data = DictField()
    # format = StringField() not needed- store in the dict and put out in formats for clients
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
    url = StringField()
    # locations = ListField(ReferenceField(Location), default=list)
    locations = ListField(StringField(max_length=96), default=list)
    service_area = ListField(ReferenceField(Location), default=list)
    moderations = ListField(EmbeddedDocumentField(Moderation), default=list)
    curations = ListField(EmbeddedDocumentField(Curation), default=list)
    tags = ListField(StringField(max_length=96), default=list)
    # _keywords = ListField(StringField(max_length=96), default=list)
    index_keys = ListField(StringField(max_length=96), default=list)
    related_resources = ListField(ReferenceField('RelatedResource'))
    added_metadata = ListField(EmbeddedDocumentField(AddedMetadata))
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

    # def __init__(self, *args, **kwargs):
    #     super(Resource, self).__init__(*args, **kwargs)
    #     print 'item __init__'
        
    def save(self, author=None, *args, **kwargs):
        self.item_metadata.last_modified = datetime.now()
        if author:
            self.item_metadata.author = author
        created = (self.id is None) # and not self.url.startswith('http://test.example.com')
        super(Resource, self).save(*args, **kwargs)
        # if created:
        #     # TODO
        #     # print 'i am new- email me'
        #     pass

    def add_locations(self, new_locations):
        """docstring for add_locations"""
        for loc in new_locations:
            if loc.loc_id not in [l.loc_id for l in self.locations]:
                self.locations.append(loc)
        
    def get_locations(self):
        return [Location.objects.get(woeid=id) for id in self.locations]
        
    def make_keys(self, keys):
        """adds self.tags to keys, uses set to make unique, then assigns to self._keywords.
           NB, item is not saved- calling code must do item.save()"""
        # keys.extend(self.tags)
        # print 'in set_keys'
        self.index_keys = list(set(keys+self.tags+self.title.split()))
        # print 'set_keys:', self.index_keys
        
    def get_keywords(self):
        return self.index_keys or []
    # keywords = property(get_keywords)

class RelatedResource(Document):
    """docstring for RelatedResource"""
    source = ReferenceField(Resource)
    target = ReferenceField(Resource)
    rel_type = StringField()
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)    

def get_nearest(lat, lon, categories=[], num=200, all_locations=False):
    """uses mongodb geo index to find num nearest locations to lat, lon parameters.
        returns list of dicts, each dict has:
        - dist (distance from lat,lon in degrees)
        - obj (dict of place attrs)
        - resources (list of resources in db at that location)"""
       
    db = get_db()
    db.eval('db.location.ensureIndex( { lat_lon : "2d" } )')
    eval_result = db.eval('db.runCommand( { geoNear : "location" , near : [%s,%s], num : %s } );' % (lat, lon, num))
    results = eval_result.get('results', [])
    
    for res in results:
        res['dis'] = res['dis'] * 111.12 # convert to Km
        if len(categories) > 0:
            # print 'using cats ', len(categories)
            res['resources'] = list(Resource.objects(locations__in=[res['obj']['woeid']],index_keys__in=categories).ensure_index('+index_keys'))
        else:
            res['resources'] = list(Resource.objects(locations__in=[res['obj']['woeid']]))
    return [res for res in results if res['resources']]


def load_resource_data(document, resource_data):
    new_data = eval(resource_data.read())
    db = get_db()
    db[document].insert(new_data)
    return db

def update_keyword_index():
    """docstring for update_keyword_index"""
    from pymongo.code import Code
    map = Code( "function () {"
                "  this.index_keys.forEach(function(z) {"
                "    emit(z, 1);"
                "  });"
                "}")

    reduce = Code("function (key, values) { return 1;}")
    # reduce = Code("function (key, values) { "
    #              "  var total = 0;"
    #              "  for (var i = 0; i < values.length; i++) {"
    #              "    total += values[i];"
    #              "  }"
    #              "  return total;"
    #              "}")
    db = get_db()
    result = db.resource.map_reduce(map, reduce, out='keyword')
    # print result
    # for res in result.find():
    #   print res

