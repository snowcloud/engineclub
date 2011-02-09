"""
http://www.aliss.scot.nhs.uk/?feed=rss2

"""
# -*- coding: UTF-8 -*-

from django import template
from django.conf import settings
from django.views.decorators.cache import cache_page

register = template.Library()

BLOG_FEED = 'http://www.aliss.scot.nhs.uk/?feed=rss2'
TWITTER_FEED = 'http://twitter.com/statuses/user_timeline/77182893.rss'


@register.tag(name="get_feed_items")
def do_feed_items(parser, token):
    """
    {% get_feed_items as items %}
    
    Based on http://djangosnippets.org/snippets/1429/
    Needs tidied to remove Delicious refs- could be made for any feed.
    And a number for entries.
    
    
    Get the last del.icio.us entries for the configured user in
    DELICIOUS_USER settings.

    Caches the result for 6 hours.
    Delicious tags is based on http://www.djangosnippets.org/snippets/819/
    """
    bits = token.contents.split()
    if len(bits) == 3 and bits[1] == 'as':
        return FeedObject(bits[2])
    else:
        return template.TemplateSyntaxError, "Invalid sytax: use get_feed_items as variable_name"
do_feed_items = cache_page(do_feed_items, 21600)

class FeedObject(template.Node):
    def __init__(self, context_variable):
        self.context_variable = context_variable

    def render(self, context):
        try:
            import feedparser
            d = feedparser.parse(BLOG_FEED)
            result=[]
            for entry in d['entries'][:min(8,len(d['entries']))]:
                title=str(entry['title'].encode('UTF-8'))
                result.append({'title':title,'link':str(entry['links'][0]['href'])})
            
        except:
            result=[]
        context[self.context_variable] = result
        return ""



