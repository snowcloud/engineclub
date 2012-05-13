# models.py

from mongoengine import *

POSTCODE = 'POSTCODE'
POSTCODEDISTRICT = 'POSTCODEDISTRICT'
OSM_PLACENAME = 'OSM_PLACENAME'
GOOGLE_PLACENAME = 'GOOGLE_PLACENAME'
ALISS_LOCATION = 'ALISS_LOCATION'


class Location(Document):
    """Location document, based on combined data sources, geonames + OSM
    loc_type = POSTCODE | POSTCODEDISTRICT | OSM_PLACENAME | GOOGLE_PLACENAME

    """
    id = StringField(primary_key=True)
    postcode = StringField()
    place_name = StringField(required=True)
    lat_lon = GeoPointField(required=True)
    loc_type = StringField(required=True)
    accuracy = IntField()
    district = StringField()
    country_code = StringField()
    edited = BooleanField(default=False)

    meta = {
        'indexes': [('place_name', 'country_code', '-accuracy')],
        'allow_inheritance': False,
        'collection': 'location'
    }
    def __unicode__(self):
        return u', '.join([self.postcode, self.place_name]) \
            if self.postcode \
            else u', '.join([self.place_name, self.district])

    @classmethod
    def create_from(cls, name):
        result = None
        C = { 'England': 'ENG', 'Scotland': 'SCT', 'Wales': 'WAL', 'other': None}
        res, addr = lookup_postcode(name)
        if addr:
            attrs = {
                'place_name': addr.get('locality', ''),
                'lat_lon': (res.geometry.location.lat, res.geometry.location.lng),
                'accuracy': 6,
                'district': addr.get('administrative_area_level_2', ''),
            }
            pc = addr.get('postal_code')
            if pc:
                attrs['postcode'] = pc
                attrs['loc_type'] = POSTCODE if len(pc) > 4 else POSTCODEDISTRICT
                attrs['id'] = pc.upper().replace(' ', '')
            else:
                attrs['loc_type'] = GOOGLE_PLACENAME
                attrs['id'] = '%s_%s' % (attrs['place_name'], attrs['district'])
            attrs['country_code'] = C.get(addr.get('administrative_area_level_1', 'other')) or addr.get('country')

            result = Location(**attrs)
            result.save()
        return result

    def perm_can_edit(self, user):
        """docstring for perm_can_edit"""
        # superuser only
        return False

    def perm_can_delete(self, user):
        """docstring for perm_can_edit"""
        # superuser only
        return False

def lookup_postcode(pc):
    from googlegeocoder import GoogleGeocoder
    geocoder = GoogleGeocoder()

    try:
        search = geocoder.get(pc, region='UK')
    except ValueError:
        return None, None
    res, addr = _make_addr(search)
    return res, addr

def _make_addr(results):

    for res in results:
        addr = {}
        for c in res.address_components:
            try:
                addr[c.__dict__['types'][0]] = c.long_name
            except IndexError:
                pass
            pc = (addr.get('postal_code') or addr.get('postal_code_prefix', '')).split()
        # if len(pc) > 1 and len(pc[1]) == 3: # full pc
        if pc: # any pc
            addr['postal_code'] = ' '.join(pc)
            break
    return res, addr
