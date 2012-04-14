import datetime

from django.contrib.auth.models import User
from django.db.models import permalink
from django.template.defaultfilters import slugify

from mongoengine import *

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
    name = StringField(max_length=100, unique=True, required=True)
    local_id = StringField(max_length=20, unique=True) # for demo, links to local user id
    email = EmailField(required=True)
    url = URLField(required=False)
    description = StringField(max_length=500)
    permissions = ListField(StringField(max_length=20))
    api_key = StringField(max_length=64)
    api_password = StringField(max_length=64)
    members = ListField(ReferenceField(Membership), default=list)
    status = StringField(max_length=12, default=STATUS_OK, required=True )
    # collections = ListField(ReferenceField('Collection'), default=list)
    in_collections = ListField(ReferenceField('Collection'), default=list)
    email_preference = StringField(choices=EMAIL_UPDATE_CHOICES, default=EMAIL_SINGLE, required=True)
    
    # FOR MOVE TO MONGOENGINE AUTH BACKEND
    # username = StringField(max_length=30, unique=True, help_text="Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters")
    # password = models.CharField(_('password'), max_length=128, help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))
    # is_staff = models.BooleanField(_('staff status'), default=False, help_text=_("Designates whether the user can log into this admin site."))
    # is_active = models.BooleanField(_('active'), default=True, help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."))
    # is_superuser = models.BooleanField(_('superuser status'), default=False, help_text=_("Designates that this user has all permissions without explicitly assigning them."))
    # last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    # date_joined = models.DateTimeField(_('date joined'), default=datetime.datetime.now)

    # password 

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
        if coll not in self.in_collections:
            self.in_collections.append(coll)
            self.save()

    def _is_staff(self):
        return User.objects.get(pk=self.local_id).is_staff
    is_staff = property(_is_staff)

    def _last_login(self):
        return User.objects.get(pk=self.local_id).last_login
    last_login = property(_last_login)

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

