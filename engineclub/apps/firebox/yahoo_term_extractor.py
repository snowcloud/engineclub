import urllib
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler

class TermExtractorApiError(Exception):
    """Exceptions for Yahoo TermExtractor API errors"""
    pass


class termextractor(object):
    """docstring for termextractor"""
    def __init__(self, api_key):
        self.api_key = api_key 
        self.url = 'http://search.yahooapis.com/ContentAnalysisService/V1/termExtraction'

    def extract_terms(self, context, query=None):
        """extract_terms sends 'data' to yahoo term extractor service and returns keywords list"""
        
        if not context:
            return []

        values = {'appid': self.api_key,
                       'context': context,
                       'query': query,
                       'output': 'json'
                       }

        data = urllib.urlencode(values)
        req = urllib2.Request(self.url, data)
        try:
            response = urllib2.urlopen(req)
            json = response.read()
        except urllib2.HTTPError, e:
            raise TermExtractorApiError(BaseHTTPRequestHandler.responses[e.code])

        # NB urllib2 will throw an exception on error, so response codes will not be used
        
        response_codes = {400: 'Bad Request',
                         404: 'Not Found',
                         413: 'Request Entity Too Large',
                         415: 'Unsupported Media Type',
                         999: 'Unable to process request at this time', }

        if response.code != 200:
           raise TermExtractorApiError('Request received a response code of %d: %s' % (response.code, response_codes[response.code]))

        response_from_json = eval(json)
        results = response_from_json.get('ResultSet', {'Result': []}).get('Result', [])

        return results
