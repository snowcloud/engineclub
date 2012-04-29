# accounts.models

from copy import deepcopy
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import permalink
from django.template.defaultfilters import slugify

from mongoengine import *
from mongoengine.queryset import QuerySet
from pysolr import Solr

from ecutils.utils import lat_lon_to_str
from locations.models import Location

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
    tags = ListField(StringField(max_length=96), default=list)
    locations = ListField(ReferenceField(Location), default=list)
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
    
    def save(self, *args, **kwargs):
        reindex = kwargs.pop('reindex', False)
        super(Account, self).save(*args, **kwargs)
        if reindex:
            self.reindex()

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

    def _collections_owned(self):
        return Collection.objects(owner=self)
    collections_owned = property(_collections_owned)

    def _is_staff(self):
        return User.objects.get(pk=self.local_id).is_staff
    is_staff = property(_is_staff)

    def perm_can_edit(self, user):
        """docstring for perm_can_edit"""
        acct = get_account(user.id)
        return self == acct

    # def perm_can_delete(self, user):
    #     """docstring for perm_can_edit"""
    #     acct = get_account(user.id)
    #     return self.owner == acct

    def _last_login(self):
        return User.objects.get(pk=self.local_id).last_login
    last_login = property(_last_login)

    def reindex(self, remove=False):
        """docstring for reindex"""
        conn = Solr(settings.SOLR_URL)
        # needs wildcard to remove indexing for multiple locations: <id>_<n>
        conn.delete(q='id:%s*' % self.id)
        if not remove:
            self.index(conn)

    def index(self, conn=None):
        """conn is Solr connection"""
        # tags = list(self.tags)
        description = [self.description]

        doc = {
            'id': unicode(self.id),
            'res_id': unicode(self.id),
            'res_type': settings.SOLR_ACCT,
            'title': self.name,
            'short_description': self.description,
            'description': u'\n'.join(description),
            'keywords': u', '.join(list(self.tags)),
            'loc_labels': [] # [', '.join([loc.label, loc.place_name]) for loc in self.locations]
        }

        result = []
        if self.locations:
            for i, loc in enumerate(self.locations):
                loc_doc = deepcopy(doc)
                loc_doc['id'] = u'%s_%s' % (unicode(self.id), i)
                loc_doc['pt_location'] = [lat_lon_to_str(loc)]
                loc_doc['loc_labels'] = [unicode(loc)]
                result.append(loc_doc)
        else:
            result = [doc]

        if conn:
            conn.add(result)
        return result

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
            if self.add_account(acct):
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
        return not found

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.owner)

    def perm_can_edit(self, user):
        """docstring for perm_can_edit"""
        acct = get_account(user.id)
        return self.owner == acct

    def perm_can_delete(self, user):
        """docstring for perm_can_edit"""
        acct = get_account(user.id)
        return self.owner == acct

def dqn_to_int(dqn):
    """
    Source: http://code.activestate.com/recipes/65219-ip-address-conversion-functions/
    Convert dotted quad notation to integer
    "127.0.0.1" => 2130706433
    """
    dqn = dqn.split(".")
    return int("%02x%02x%02x%02x" % (int(dqn[0]), int(dqn[1]), int(dqn[2]), int(dqn[3])), 16)


def int_to_dqn(i):
    """
    Source: http://code.activestate.com/recipes/65219-ip-address-conversion-functions/
    Convert integer to dotted quad notation
    """
    i = "%08x" % (i)
    ###
    # The same issue as for `dqn_to_int()`
    ###
    return "%i.%i.%i.%i" % (int(i[0:2], 16), int(i[2:4], 16), int(i[4:6], 16), int(i[6:8], 16))


class AccountIPRange(Document):
    owner = ReferenceField('Account', required=True)
    ip_min = IntField()
    ip_max = IntField()

    def __unicode__(self):
        return "%s - %s - %s" % (self.owner, int_to_dqn(self.ip_min), int_to_dqn(self.ip_max))


class SavedSearch(Document):

    owner = ReferenceField('Account', required=True, unique=True)
    terms = ListField(StringField(max_length=40))

    def __unicode__(self):
        return u"%s's saved searches" % self.owner
