from mongoengine import *

# Create your models here.

class Setting(Document):
    key = StringField(primary_key=True)
    value = DictField(default={})

    meta = {
        # 'indexes': [('k', 'country_code', '-accuracy')],
        'allow_inheritance': False,
    }

