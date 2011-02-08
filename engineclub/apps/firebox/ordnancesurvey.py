# ordnancesurvey.py
# utility stuff for managing OS data
# author Derek Hoy


import simplejson, urllib
POSTCODE_BASE = 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/%s.json'

# this for eg EH15, could try next if postcode fails
POSTCODEDISTRICT_BASE = 'http://data.ordnancesurvey.co.uk/doc/postcodedistrict/%s.json'
#  eg, EH
POSTCODEAREA_BASE = 'http://data.ordnancesurvey.co.uk/doc/postcodearea/%s.json'


OS_LABEL = 'http://www.w3.org/2000/01/rdf-schema#label'
OS_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
OS_LAT = 'http://www.w3.org/2003/01/geo/wgs84_pos#lat'
OS_LON = 'http://www.w3.org/2003/01/geo/wgs84_pos#long'
OS_WARD = 'http://data.ordnancesurvey.co.uk/ontology/postcode/ward'
OS_DISTRICT = 'http://data.ordnancesurvey.co.uk/ontology/postcode/district'
OS_COUNTRY = 'http://data.ordnancesurvey.co.uk/ontology/postcode/country'


# def search(query, results=20, start=1, **kwargs):
#     kwargs.update({
#         'appid': APP_ID,
#         'query': query,
#         'results': results,
#         'start': start,
#         'output': 'json'
#     })
#     url = SEARCH_BASE + '?' + urllib.urlencode(kwargs)
#     result = simplejson.load(urllib.urlopen(url))
#     if 'Error' in result:
#         # An error occurred; raise an exception
#         raise YahooSearchError, result['Error']
#     return result['ResultSet']

def get_postcode(postcode, testing=False):
    """docstring for get_postcode"""
    postcode = postcode.upper().replace(' ', '')
    url = POSTCODE_BASE % postcode
    loc_id = result = None
    # print 'searching...\n'
    if postcode:
        if not testing:
            try:
                page = urllib.urlopen(url)
            except IOError:
                return None, 'could not open service URL'
            try:
                json_result = simplejson.load(page)
            except ValueError:
                return None, 'no result from Ord Survey, probably did not find postcode [%s]' % (postcode or '-')
            loc_id = 'http://data.ordnancesurvey.co.uk/id/postcodeunit/%s' % postcode
        else:
            print 'TEST RUN- NOT LIVE DATA'
            json_result = {'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.html': {'http://purl.org/dc/terms/title': [{'type': 'literal', 'value': 'Linked Data in HTML format for EH15 2QR'}], 'http://xmlns.com/foaf/0.1/primaryTopic': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR'}], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': [{'type': 'uri', 'value': 'http://purl.org/dc/dcmitype/Text'}, {'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/Document'}], 'http://purl.org/dc/terms/isFormatOf': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR'}], 'http://purl.org/dc/terms/format': [{'type': 'literal', 'value': 'text/html'}]}, 'http://data.ordnancesurvey.co.uk/ontology/postcode/PostcodeUnit': {'http://www.w3.org/2000/01/rdf-schema#label': [{'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'type': 'literal', 'value': 'Postcode Unit'}], 'http://www.w3.org/2000/01/rdf-schema#comment': [{'type': 'literal', 'value': 'An area covered by a particular postcode. Postcodes are an alphanumeric abbreviated form of address. Postcode units are unique references and identify an average of 15 addresses. In some cases, where an address receives a substantial amount of mail, a postcode will apply to only one address (a large-user postcode). The maximum number of addresses in a postcode is 100.\n\nA sub-area of a postcode sector, indicated by the two letters of the inward postcode, which identifies one or more small-user postcode delivery points or an individual large-user postcode. There are approximately 1.7 million postcode units in the UK.'}]}, 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.rdf': {'http://purl.org/dc/terms/title': [{'type': 'literal', 'value': 'Linked Data in RDF/XML format for EH15 2QR'}], 'http://xmlns.com/foaf/0.1/primaryTopic': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR'}], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': [{'type': 'uri', 'value': 'http://purl.org/dc/dcmitype/Text'}, {'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/Document'}], 'http://purl.org/dc/terms/isFormatOf': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR'}], 'http://purl.org/dc/terms/format': [{'type': 'literal', 'value': 'application/rdf+xml'}]}, 'http://data.ordnancesurvey.co.uk/id/7000000000043410': {'http://www.w3.org/2000/01/rdf-schema#label': [{'type': 'literal', 'value': 'Portobello/Craigmillar'}], 'http://www.w3.org/2004/02/skos/core#prefLabel': [{'type': 'literal', 'value': 'Portobello/Craigmillar'}]}, 'http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR': {'http://data.ordnancesurvey.co.uk/ontology/postcode/RH': [{'type': 'literal', 'value': 'S00'}], 'http://www.w3.org/2004/02/skos/core#notation': [{'datatype': 'http://data.ordnancesurvey.co.uk/ontology/postcode/Postcode', 'type': 'literal', 'value': 'EH15 2QR'}], 'http://www.georss.org/georss/point': [{'type': 'literal', 'value': '55.945354 -3.101903'}], 'http://data.ordnancesurvey.co.uk/ontology/postcode/district': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/7000000000030505'}], 'http://data.ordnancesurvey.co.uk/ontology/spatialrelations/northing': [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '673028'}], 'http://data.ordnancesurvey.co.uk/ontology/postcode/country': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/country/scotland'}], 'http://data.ordnancesurvey.co.uk/ontology/spatialrelations/easting': [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '331278'}], 'http://data.ordnancesurvey.co.uk/ontology/postcode/ward': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/7000000000043410'}], 'http://data.ordnancesurvey.co.uk/ontology/spatialrelations/within': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodedistrict/EH15'}, {'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodearea/EH'}, {'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodesector/EH152'}], 'http://www.w3.org/2003/01/geo/wgs84_pos#long': [{'datatype': 'http://www.w3.org/2001/XMLSchema#decimal', 'type': 'literal', 'value': '-3.101903'}], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/ontology/postcode/PostcodeUnit'}], 'http://www.w3.org/2003/01/geo/wgs84_pos#lat': [{'datatype': 'http://www.w3.org/2001/XMLSchema#decimal', 'type': 'literal', 'value': '55.945354'}], 'http://www.w3.org/2000/01/rdf-schema#label': [{'type': 'literal', 'value': 'EH15 2QR'}], 'http://data.ordnancesurvey.co.uk/ontology/postcode/PQ': [{'type': 'literal', 'value': '10'}], 'http://data.ordnancesurvey.co.uk/ontology/postcode/LH': [{'type': 'literal', 'value': 'SS9'}]}, 'http://data.ordnancesurvey.co.uk/id/7000000000030505': {'http://www.w3.org/2000/01/rdf-schema#label': [{'type': 'literal', 'value': 'The City of Edinburgh'}], 'http://www.w3.org/2004/02/skos/core#prefLabel': [{'type': 'literal', 'value': 'The City of Edinburgh'}]}, 'http://data.ordnancesurvey.co.uk/id/postcodedistrict/EH15': {'http://www.w3.org/2000/01/rdf-schema#label': [{'type': 'literal', 'value': 'EH15'}]}, 'http://data.ordnancesurvey.co.uk/id/postcodesector/EH152': {'http://www.w3.org/2000/01/rdf-schema#label': [{'type': 'literal', 'value': 'EH15 2'}]}, 'http://data.ordnancesurvey.co.uk/id/country/scotland': {'http://www.w3.org/2000/01/rdf-schema#label': [{'lang': 'en', 'type': 'literal', 'value': 'Scotland'}], 'http://www.w3.org/2004/02/skos/core#prefLabel': [{'type': 'literal', 'value': 'Scotland'}]}, 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR': {'http://purl.org/dc/terms/title': [{'type': 'literal', 'value': 'Linked Data for EH15 2QR'}], 'http://xmlns.com/foaf/0.1/primaryTopic': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR'}], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': [{'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/Document'}, {'type': 'uri', 'value': 'http://purl.org/dc/dcmitype/Text'}], 'http://purl.org/dc/terms/hasFormat': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.rdf'}, {'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.html'}, {'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.json'}, {'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.ttl'}]}, 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.json': {'http://purl.org/dc/terms/title': [{'type': 'literal', 'value': 'Linked Data in RDF/JSON format for EH15 2QR'}], 'http://xmlns.com/foaf/0.1/primaryTopic': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR'}], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': [{'type': 'uri', 'value': 'http://purl.org/dc/dcmitype/Text'}, {'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/Document'}], 'http://purl.org/dc/terms/isFormatOf': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR'}], 'http://purl.org/dc/terms/format': [{'type': 'literal', 'value': 'application/json'}]}, 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR.ttl': {'http://purl.org/dc/terms/title': [{'type': 'literal', 'value': 'Linked Data in Turtle format for EH15 2QR'}], 'http://xmlns.com/foaf/0.1/primaryTopic': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR'}], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': [{'type': 'uri', 'value': 'http://purl.org/dc/dcmitype/Text'}, {'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/Document'}], 'http://purl.org/dc/terms/isFormatOf': [{'type': 'uri', 'value': 'http://data.ordnancesurvey.co.uk/doc/postcodeunit/EH152QR'}], 'http://purl.org/dc/terms/format': [{'type': 'literal', 'value': 'text/plain'}]}, 'http://data.ordnancesurvey.co.uk/id/postcodearea/EH': {'http://www.w3.org/2000/01/rdf-schema#label': [{'type': 'literal', 'value': 'EH'}]}}
            loc_id = 'http://data.ordnancesurvey.co.uk/id/postcodeunit/EH152QR'

        data = json_result[loc_id]
        items = [ OS_LABEL, OS_TYPE, OS_LAT, OS_LON, OS_WARD, OS_DISTRICT, OS_COUNTRY ]

        # print loc_id, '\n========'
        result = {}
        for value in items:
            try:
                result[value]= data[value][0]['value']
            except KeyError:
                # occasional post code has missing data, eg KY122BB
                pass
    else:
        result = 'no postcode'
    return loc_id, result


if __name__ == "__main__":
    # print get_postcode('eh12 5')
    # print get_postcode('eh12 5l')
    print get_postcode('eh12 5lr')
    