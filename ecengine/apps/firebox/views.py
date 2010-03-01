# Create your views here.
from django.conf import settings
import urllib
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler # import responses
from BeautifulSoup import BeautifulSoup

# probably move this code to utils.py if enough
def get_url_content(url):
    try:
        response = urllib2.urlopen(url)
        htmltext = response.read()
    except urllib2.HTTPError, e:
        raise Exception(BaseHTTPRequestHandler.responses[e.code])
    
    soup = BeautifulSoup(htmltext)
    result = ''.join([e for e in soup.recursiveChildGenerator() if isinstance(e,unicode)])
    return result.encode('ascii', 'ignore')

from placemaker.placemaker import placemaker

def geomaker(content):
    if content.startswith('http'):
        data = get_url_content(content)
    else:
        data = content
    p = placemaker(settings.YAHOO_KEY)
    p.find_places(data)
    return p