# from django.conf import settings
# from django.contrib.auth.views import login
# from django.contrib.flatpages.models import FlatPage
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import render_to_response
# from django.template import RequestContext, loader

# import urlparse

from django.core.urlresolvers import resolve, Resolver404
import httpagentparser
from analytics.models import AccountAnalytics

# class HttpResponseServiceUnavailable(HttpResponse):
#     status_code = 503
    
class AnalyticsMiddleware(object):
    """
    Engineclub analytics middleware.
    
    """
    def __init__(self):
    	pass
        # self.template = getattr(settings, 'SITEDOWN_TEMPLATE', 'sitedown/default.html' )
        # self.disabled = getattr(settings, 'SITEDOWN_DISABLE', False)
        # self.static_url = getattr(settings, 'STATIC_URL', False)
        # self.redirect = getattr(settings, 'SITEDOWN_REDIRECT', '/sitedown/')
        # self.use_302 = getattr(settings, 'SITEDOWN_USE_302', False)
        # self.flatpage = getattr(settings, 'SITEDOWN_FLATPAGE', False)
        
    def process_request(self, request):
    	"""
    	request.META
			CONTENT_LENGTH -- the length of the request body (as a string).
			CONTENT_TYPE -- the MIME type of the request body.
			HTTP_ACCEPT_ENCODING -- Acceptable encodings for the response.
			HTTP_ACCEPT_LANGUAGE -- Acceptable languages for the response.
			HTTP_HOST -- The HTTP Host header sent by the client.
			HTTP_REFERER -- The referring page, if any.
			HTTP_USER_AGENT -- The client's user-agent string.
			QUERY_STRING -- The query string, as a single (unparsed) string.
			REMOTE_ADDR -- The IP address of the client.
			REMOTE_HOST -- The hostname of the client.
			REMOTE_USER -- The user authenticated by the Web server, if any.
			REQUEST_METHOD -- A string such as "GET" or "POST".
			SERVER_NAME -- The hostname of the server.
			SERVER_PORT -- The port of the server (as a string).
    	"""
        analytics = AccountAnalytics(None)
        log = True

        META_KEYS = ['HTTP_USER_AGENT', ]
        for key in META_KEYS:
            value = request.META.get(key)
            if value:
                if key == 'HTTP_USER_AGENT':
                    try:
                        # parser.detect gives more detail- could break out into OS, browser, version stats...
                        # simple_detect -> ('Linux', 'Chrome 5.0.307.11')
                        value = httpagentparser.simple_detect(value)[1]
                        log = value != 'Unknown Browser'
                    except IndexError:
                        pass
                analytics.increment(key, field=value)

        request.META["ENGINE_LOG"] = log
        if log:
            DETAIL_PATHS = ['resource', 'accounts_detail']
            try:
                match = resolve(request.path)
                # print match.url_name, match.args, match.kwargs
                if match.url_name in DETAIL_PATHS and 'object_id' in match.kwargs:
                    analytics.increment(match.url_name, field=match.kwargs['object_id'])

            except Resolver404:
                pass

    	
    	return None
        
