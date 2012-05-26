# from django.conf import settings
# from django.contrib.auth.views import login
# from django.contrib.flatpages.models import FlatPage
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import render_to_response
# from django.template import RequestContext, loader

# import urlparse

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
    	# print request.path
    	# print request.META.get('HTTP_USER_AGENT')
    	
    	return None

        # if  self.disabled or \
        #     request.path.startswith('/admin') or \
        #     request.path.startswith(urlparse.urlparse(settings.MEDIA_URL).path) or \
        #     (self.static_url and request.path.startswith(urlparse.urlparse(settings.STATIC_URL).path)):
        #     return None
        # if request.path == self.redirect:
        #     return render_to_response(self.template,
        #         RequestContext( request, {}))
        # if self.use_302:
        #     return HttpResponseRedirect(self.redirect)
        # else:
        #     response = HttpResponseServiceUnavailable(mimetype='text/html')
        #     t = loader.get_template(self.template)
        #     if self.flatpage:
        #         fp = FlatPage.objects.get(url=self.flatpage)
        #         title = fp.title
        #         message = fp.content
        #     else:
        #         title = message = ''
        #     response.write(t.render(RequestContext( request, { 'title': title, 'message': message })))
        #     return response
        
