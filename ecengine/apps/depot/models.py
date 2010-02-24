# from django.db import models


from mongoengine import *
from datetime import datetime

COLL_STATUS_NEW = 'new'
COLL_STATUS_LOC_CONF = 'location_confirm'
COLL_STATUS_ = ''
COLL_STATUS_ = ''
COLL_STATUS_COMPLETE = 'complete'
# COLLECTION_STATUS = ('new', )

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

    def save(self, *args, **kwargs):
        created = (self.id is None) and not self.url.startswith('http://test.example.com')
        super(Item, self).save(*args, **kwargs)
        if created:
            print 'i am new- email me'
   
from django.utils.simplejson import *
from ecutils.utils import dict_to_string_keys

def load_item_data(item_data):
    items = load(item_data)
    for item in items:
        # can't pass in item dict as kwargs cos won't take unicode keys
        Item.objects.get_or_create(**dict_to_string_keys(item))
