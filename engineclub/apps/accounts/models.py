import datetime

from django.db.models import permalink
from django.template.defaultfilters import slugify

from mongoengine import *
from mongoengine.django.auth import User

# dependancy loop
# from depot.models import Location

MEMBER_ROLE = 'member'
ADMIN_ROLE = 'admin'
MENTOR_ROLE = 'mentor'
STATUS_OK = 'ok'
STATUS_SUSPENDED = 'suspended'
STATUS_CLOSED = 'closed'


def get_account(local_id):
    """docstring for get_account"""
    try:
        return Account.objects.get(local_id=str(local_id))
    except Account.DoesNotExist:
        return None

class Membership(Document):
    member = ReferenceField('Account', required=True)
    parent_account= ReferenceField('Account', required=True)
    role = StringField(max_length=20, required=True, default=MEMBER_ROLE)

    meta = {
        'allow_inheritance': False
    }

    def __unicode__(self):
        return u'%s, %s' % (self.member.name, self.role)


EMAIL_NONE, EMAIL_SINGLE, EMAIL_DIGEST = (
    'none', 'single', 'digest')
EMAIL_UPDATE_CHOICES= ((EMAIL_NONE, 'No updates'), (EMAIL_SINGLE, 'Single emails'), (EMAIL_DIGEST, 'Daily digest'))

class Account(Document):
    """
    An account can be held 
    
    """
    name = StringField(max_length=100, required=True)
    local_id = StringField(max_length=20, unique=True) # for demo, links to local user id
    email = EmailField(required=True)
    url = URLField(required=False)
    description = StringField(max_length=500)
    permissions = ListField(StringField(max_length=20))
    api_key = StringField(max_length=64)
    api_password = StringField(max_length=64)
    members = ListField(ReferenceField(Membership), default=list)
    status = StringField(max_length=12, default=STATUS_OK, required=True )
    collections = ListField(ReferenceField('Collection'), default=list)
    email_preference = StringField(choices=EMAIL_UPDATE_CHOICES, default=EMAIL_SINGLE, required=True)

    meta = {
        'ordering': ['name'],
        'allow_inheritance': False
    }

    # created_by = ReferenceField(User)
    # created_at = DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.name
    
    def add_member(self, member, role=MEMBER_ROLE):
        found = False
        for obj in self.members:
            found = obj.member.id == member.id
            if found:
                break
        if not found:
            m = Membership.objects.create(member=member, parent_account=self, role=role)
            self.members.append(m)

    def add_to_collection(self, coll):
        if coll not in self.collections:
            self.collections.append(coll)
            self.save()

class CollectionMember(Document):
    account = ReferenceField('Account', required=True)
    collection= ReferenceField('Collection', required=True)
    role = StringField(max_length=20, required=True, default=MEMBER_ROLE)

    meta = {
        'allow_inheritance': False
    }

    def __unicode__(self):
        return u'%s, %s' % (self.account.name, self.role)

class Collection(Document):
    """
    An account can be held 
    
    """
    name = StringField(max_length=100, required=True)
    owner = ReferenceField('Account', required=True)
    tags = ListField(StringField(max_length=96), default=list)
    # locations = ListField(ReferenceField(Location), default=list)
    accounts = ListField(ReferenceField(CollectionMember), default=list)

    meta = {
        'ordering': ['name'],
        'allow_inheritance': False
    }

    def add_accounts(self, accts, role=MEMBER_ROLE):
        for acct in accts:
            self.add_account(acct)
            acct.add_to_collection(self)

    def add_account(self, acct, role=MEMBER_ROLE):
        found = False
        for obj in self.accounts:
            found = obj.account.id == acct.id
            if found:
                break
        if not found:
            m = CollectionMember.objects.create(account=acct, collection=self, role=role)
            self.accounts.append(m)

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.owner)

