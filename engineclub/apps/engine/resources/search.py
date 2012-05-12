# search.py
import re

from django.conf import settings
from mongoengine.connection import _get_db as get_db
from pymongo import Connection, DESCENDING, ASCENDING, GEO2D
from pysolr import Solr

from ecutils.utils import minmax, lat_lon_to_str


###############################################################
# LOCATION STUFF - PUBLIC

def get_location(namestr, dbname=settings.MONGO_DATABASE_NAME, just_one=True, starts_with=False):
    """
    namestr can be postcode, placename, or 'placename: district' for places with same name
    """
    # could do lat_lon search by testing namestr for '123.456, 123.456'
    # split on ','
    # check len=2
    # check parts 1 and 2 (trimmed) convert to real
    # return {'lat_lon': [real, real] }

    db = get_db()
    coll = db.location
    district =None
    if len(namestr) > 2 and namestr[2].isdigit():
        name = namestr.upper().replace(' ', '').strip()
        field = '_id'
    else:
        names = [n.strip() for n in namestr.split(':')]
        name = names[0]
        district = names[1] if len(names) > 1 else None
        field = 'place_name'
        coll.ensure_index([
            ('place_name', ASCENDING),
            ('country_code', ASCENDING),
            ('accuracy', DESCENDING)
            ])

    # removed this- supposed to be slow cos index not used
    # but seems ok, and improves usability
    # if starts_with:
    name = re.compile('^%s' % name, re.IGNORECASE)
    find_dict = {field: name}
    if district:
        find_dict['district'] = district
    result = coll.find_one(find_dict) if just_one else coll.find(find_dict).limit(20)
    if result and (type(result) == dict or result.count() > 0):

        return result
    else:
        return []


###############################################################
# SEARCH STUFF

"""
from pysolr.py

class Results(object):
    def __init__(self, docs, hits, highlighting=None, facets=None, spellcheck=None, stats=None, qtime=None, debug=None):
        self.docs = docs
        self.hits = hits
        self.highlighting = highlighting or {}
        self.facets = facets or {}
        self.spellcheck = spellcheck or {}
        self.stats = stats or {}
        self.qtime = qtime
        self.debug = debug or {}

    def __len__(self):
        return len(self.docs)

    def __iter__(self):
        return iter(self.docs)

"""

def _make_fq(event, accounts, collections, res_type):
    fq = ['res_type:%s' % res_type]
    if event:
        fq.append('(event_start:[NOW/DAY TO *] OR event_end:[NOW/DAY TO *])')
    if accounts:
        fq.append('accounts:(%s)'% ' OR '.join(accounts))
    if collections:
        fq.append('collections:(%s)'% ' OR '.join(collections))
    if fq:
        return ' AND '.join(fq)
    return None


def find_by_place(name, kwords, loc_boost=None, start=0, max=None, accounts=None, collections=None, event=None, res_type=settings.SOLR_RES):
    loc = get_location(name)
    if loc:
        kw = {
            'start': start,
            'rows': minmax(0, settings.SOLR_ROWS, max, settings.SOLR_ROWS),
            'fl': '*,score',
            # 'fq': 'accounts:(4d9c3ced89cb162e5e000000 OR 4d9b99d889cb16665c000000) ',
            'qt': 'resources',
            'sfield': 'pt_location',
            'pt': lat_lon_to_str(loc['lat_lon']),
            'bf': 'recip(geodist(),2,200,20)^%s' % (loc_boost or settings.SOLR_LOC_BOOST_DEFAULT),
            'sort': 'score desc',
        }
        fq =  _make_fq(event, accounts, collections, res_type)
        if fq:
            kw['fq'] = fq

        conn = Solr(settings.SOLR_URL)
        return loc['lat_lon'], conn.search(kwords.strip() if kwords else '', **kw)
    else:
        return None, None

def find_by_place_or_kwords(name, kwords, loc_boost=None, start=0, max=None, accounts=None, collections=None, event=None, res_type=settings.SOLR_RES):
    """docstring for find_by_place_or_kwords"""
    if name:
        return find_by_place(name, kwords, loc_boost, start, max, accounts, collections, event, res_type)
    # keywords only
    kw = {
        'start': start,
        'rows': minmax(0, settings.SOLR_ROWS, max, settings.SOLR_ROWS),
        'fl': '*,score',
        'qt': 'resources',
    }
    fq =  _make_fq(event, accounts, collections, res_type)
    # example 'fq': '(event_start:[NOW/DAY TO *] OR event_end:[NOW/DAY TO *]) AND accounts:4d9b99d889cb16665c000000'
    if fq:
        kw['fq'] = fq

    conn = Solr(settings.SOLR_URL)
    return None, conn.search(kwords.strip() if kwords else '', **kw)
