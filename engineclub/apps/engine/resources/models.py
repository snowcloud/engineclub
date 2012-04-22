# resources.models

from copy import deepcopy
from datetime import datetime

from django.conf import settings

from mongoengine import *
from mongoengine.connection import _get_db as get_db
from pysolr import Solr

from accounts.models import Account, get_account
from ecutils.utils import lat_lon_to_str
from locations.models import Location


COLL_STATUS_NEW = 'new'
COLL_STATUS_LOC_CONF = 'location_confirm'
COLL_STATUS_TAGS_CONF = 'tags_confirm'
COLL_STATUS_ = ''
COLL_STATUS_COMPLETE = 'complete'

STATUS_OK = 'OK'
STATUS_BAD = 'BAD'
STATUS_CHOICES = (
    (STATUS_OK, 'OK'),
    (STATUS_BAD, 'Bad')
    )

import logging
logger = logging.getLogger('aliss')

class ItemMetadata(EmbeddedDocument):
    last_modified = DateTimeField(default=datetime.now)
    author = ReferenceField(Account)
    shelflife = DateTimeField(default=datetime.now) # TODO set to now + settings.DEFAULT_SHELFLIFE
    status = StringField()
    note = StringField()

    def update(self, author, last_modified=None):
        """docstring for update"""
        self.author = author
        self.last_modified = last_modified or datetime.now()

class CalendarEvent(EmbeddedDocument):
    """used to add event data to Resource. Subset of W3C Calendar API: http://www.w3.org/TR/calendar-api/"""
    start = DateTimeField()
    end = DateTimeField()
    status = StringField(default='confirmed') # 'provisional', 'confirmed', 'cancelled'.
    # recurrence = EmbeddedDocumentField(CalendarRepeatRule)

class Moderation(EmbeddedDocument):
    outcome = StringField()
    note = StringField()
    owner = ReferenceField(Account)
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

class Curation(Document):
    outcome = StringField()
    tags = ListField(StringField(max_length=96), default=list)
    # rating - not used
    note = StringField()
    data = DictField()
    resource = ReferenceField('Resource')
    owner = ReferenceField(Account)
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

    def perm_can_edit(self, user):
        """docstring for perm_can_edit"""
        acct = get_account(user.id)
        return self.owner == acct

    def perm_can_delete(self, user):
        """docstring for perm_can_edit"""
        acct = get_account(user.id)
        return self.owner == acct

class Resource(Document):
    """ Main model for ALISS resource """
    title = StringField(required=True)
    description = StringField(default='')
    resource_type = StringField()
    uri = StringField()
    locations = ListField(ReferenceField(Location), default=list)
    service_area = ListField(ReferenceField(Location), default=list)
    calendar_event = EmbeddedDocumentField(CalendarEvent)
    moderations = ListField(EmbeddedDocumentField(Moderation), default=list)
    curations = ListField(ReferenceField(Curation), default=list)
    tags = ListField(StringField(max_length=96), default=list)
    related_resources = ListField(ReferenceField('RelatedResource'))
    owner = ReferenceField(Account, required=True)
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)
    status = StringField(choices=STATUS_CHOICES, default=STATUS_OK, required=True)

    @classmethod
    def reindex_for(cls, acct):
        for c in Curation.objects(owner=acct):
            c.resource.reindex()

    def save(self, *args, **kwargs):
        reindex = kwargs.pop('reindex', False)
        author = kwargs.pop('author', None)
        created = self.id is None
        super(Resource, self).save(*args, **kwargs)
        self.item_metadata.update(author or self.owner)
        if created:
            if not self.moderations:
                obj = Moderation(outcome=STATUS_OK, owner=self.owner)
                obj.item_metadata.author = self.owner
                self.moderations.append(obj)
            if not self.curations:
                obj = Curation(outcome=STATUS_OK, tags=self.tags, owner=self.owner)
                obj.item_metadata.author = self.owner
                obj.resource = self
                obj.save()
                self.curations.append(obj)
            super(Resource, self).save(*args, **kwargs)

        if reindex:
            self.reindex()

    def delete(self, *args, **kwargs):
        """docstring for delete"""
        for c in self.curations:
            c.delete()
        self.reindex(remove=True)
        super(Resource, self).delete(*args, **kwargs)

    def add_curation(self, curation, reindex=True):
        """
        pass in new Curation, it will be linked and saved.
        Failed in 0.6.0, so disabled
        """
        raise Exception('Do not use resource.add_curation- mongoengine problem updating lists. Use add_curation function')
        # curation.resource = self
        # curation.save()
        # c = deepcopy(self.curations)
        # c.append(curation)
        # self.curations = c
        # # self.curations.append(curation)
        # self.save(reindex=reindex)

    def _all_tags(self):
        tags = self.tags
        for c in self.curations:
            tags.extend(c.tags)
        return list(set(tags))
    all_tags = property(_all_tags)

    def get_curation_for_acct(self, account):
        # check if user already has a curation for this resource
        if account:
            for index, obj in enumerate(self.curations):
                if obj.owner.id == account.id:
                    return index, obj
        return None, None

    def get_moderation_for_acct(self, account):
        # check if user already has a moderation for this resource
        if account:
            for index, obj in enumerate(self.moderations):
                if obj.owner.id == account.id:
                    return index, obj
        return None, None

    def moderate_as_bad(self, account, remove_old=True):
        if remove_old:
            self.remove_bad_mod(save=False)
        _, mod = self.get_moderation_for_acct(account)
        if mod is None:
            mod = Moderation(outcome=STATUS_BAD, owner=account)
            mod.item_metadata.author = account
            self.moderations.append(mod)
            self.status = STATUS_BAD
        self.save()
        self.reindex(remove=True)

    def remove_bad_mod(self, save=True):
        self.moderations = [mod for mod in self.moderations if mod.outcome != STATUS_BAD]
        self.status = STATUS_OK
        if save:
            self.save()

    def _status_is_bad(self):
        return self.status == STATUS_BAD
    status_is_bad = property(_status_is_bad)

    def reindex(self, remove=False):
        """docstring for reindex"""
        conn = Solr(settings.SOLR_URL)
        # needs wildcard to remove indexing for multiple locations: <id>_<n>
        conn.delete(q='id:%s*' % self.id)
        if not remove:
            self.index(conn)

    def index(self, conn=None):
        """conn is Solr connection"""
        if self.status == STATUS_BAD:
            return None
        tags = list(self.tags)
        accounts = []
        collections = []
        description = [self.description]

        # try:

        for obj in self.curations:
            tags.extend(obj.tags)
            accounts.append(unicode(obj.owner.id))
            if hasattr(obj.owner, 'collections'):
                collections.extend(obj.owner.in_collections)
            description.extend([obj.note or u'', unicode(obj.data) or u''])

        # except AttributeError:
        #     logger.error("fixed error in curations while indexing resource: %s, %s" % (self.id, self.title))
        #     self.curations = []
        #     self.save()
        doc = {
            'id': unicode(self.id),
            'res_id': unicode(self.id),
            'title': self.title,
            'short_description': self.description,
            'description': u'\n'.join(description),
            'keywords': u', '.join(list(set(tags))),
            'accounts': u', '.join(accounts),
            'collections': u', '.join(set([str(c.id) for c in collections])),
            'uri': self.uri,
            'loc_labels': [] # [', '.join([loc.label, loc.place_name]) for loc in self.locations]
        }
        if self.calendar_event:
            doc['event_start'] = self.calendar_event.start #.date()
            if self.calendar_event.end:
                doc['event_end'] = self.calendar_event.end #.date()
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

    def perm_can_edit(self, user):
        """docstring for perm_can_edit"""
        acct = get_account(user.id)
        return self.owner == acct

    def perm_can_delete(self, user):
        """docstring for perm_can_edit"""
        acct = get_account(user.id)
        return self.owner == acct

class RelatedResource(Document):
    """docstring for RelatedResource"""
    source = ReferenceField(Resource)
    target = ReferenceField(Resource)
    rel_type = StringField()
    item_metadata = EmbeddedDocumentField(ItemMetadata,default=ItemMetadata)

def add_curation(resource, curation, reindex=True):
    curation.resource = resource
    curation.save()
    resource.curations.append(curation)
    resource.save(reindex=reindex)

def load_resource_data(document, resource_data):
    new_data = eval(resource_data.read())
    db = get_db()
    db[document].insert(new_data)
    return db

