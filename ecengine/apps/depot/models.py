# from django.db import models


from mongoengine import *
from datetime import datetime

class Item(Document):
    url = StringField(unique=True, required=True)
    title = StringField(required=True)
    description = StringField()
    postcode = StringField()
    area = StringField()
    tags = StringField()
    last_modified = DateTimeField(default=datetime.now)
    shelflife = StringField()
    source = StringField()
    status = StringField()
    admin_note = StringField()

   
from django.utils.simplejson import *

def load_item_data(item_data):
    pass
    items = load(item_data)
    for item in items:
        # can't pass in dict as kwargs cos won't take unicode strings
        Item.objects.get_or_create(**{'url': item['url'], 'title': item['title']})
