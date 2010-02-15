# from django.db import models


from mongoengine import *
import datetime

class Item(Document):
    name = StringField(unique=True, required=True)

   
# class Item(models.Model):
# 
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(blank=True, max_length=80)
#     
#     class Meta:
#         # data will be in mongodb
#         managed = False
# 
#     def save(self, *args, **kwargs):
#         pass
#         print kwargs.get('db', 'defaultdb') # read this from settings
#         print 'saving: %s' % self.name
#         
#     def __unicode__(self):
#         return '%s: %s' % (self.id, self.name)
#   
   
# from django.core import serializers
from django.utils.simplejson import *

def load_item_data(item_data):
    pass
    items = load(item_data)
    for item in items:
        Item.objects.get_or_create(name=item['name'])
