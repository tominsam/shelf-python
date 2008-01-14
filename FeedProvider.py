from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLinkFromHTMLSource
import urllib, urlparse
import time

from Utilities import _info

class FeedProvider( Provider ):

    def provide( self ):
        self.urls() # if we're pulling from boring_urls, do it first
        self.start()
        
    def guardedRun(self):
        pool = NSAutoreleasePool.alloc().init()

        todo = self.urls()
        if not todo: return

        self.atoms = [ self.htmlForPending(url, False) for url in todo ]

        for index in range(0, len(todo)):
            url = todo[index]

            self.atoms[index] = self.htmlForPending(url, True)
            self.changed()

            stale = self.getFeed( url, stale = True )
            if stale: # we've seen this before
                self.atoms[index] = self.htmlForFeed( url, stale, True )
            else:
                self.atoms[index] = self.htmlForPending(url, True)
            self.changed()
            
            fresh = self.getFeed( url, stale = False )
            if fresh: # feed is good
                self.atoms[index] = self.htmlForFeed( url, fresh, False )
            else:
                self.atoms[index] = ""
            self.changed()

    def getFeed( self, url, stale = False ):
        rss, username, password = self.feed_for_url( url )
        if not rss:
            return None

        if stale:
            data = self.staleUrl( rss, username = username, password = password )
        else:
            data = self.cacheUrl( rss, timeout = self.timeout(), username = username, password = password )
        if not data:
            return

        feed = feedparser.parse( data )
        if feed and 'feed' in feed and 'title' in feed.feed:
            return feed
        else: 
            return None





    # override these
    
    def timeout(self):
        return 60 * 20
        
    def feed_for_url( self, url ):
        # it's very unlikely that the feed source will move
        rss = getRSSLinkFromHTMLSource( self.cacheUrl( url, timeout = 3600 * 10 ) )
        rss = urlparse.urljoin( url, rss )
        return rss, None, None
    
    def urls(self):
        return self.person.boring_urls
    
    def htmlForPending( self, url, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.spinner()
        else:
            spinner_html = ""
        return "<h3><a href='%s'>%s%s</a></h3>"%(url,url,spinner_html)
   
    
    def htmlForFeed( self, url, feed, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.spinner()
        else:
            spinner_html = ""
        html = "<h3><a href='%s'>%s%s</a></h3>"%( url, feed.feed.title, spinner_html )
        entries = feed.entries
        for item in entries[0:4]:
            if 'published_parsed' in item:
                html += '<span class="feed-date">%s</span>'%( time.strftime("%b %d", item.published_parsed ) )
            html += '<p class="feed-title"><a href="%s">%s</a></p>'%( item.link, item.title )
            detail = None
            if 'content' in item and len(item.content) > 0:
                detail = item.content[0].value
            elif 'summary' in item and len(item.summary) > 0:
                detail = item.summary
            if detail:
                raw = re.sub(r'<.*?>', '', detail) # strip tags
                trimmed = " ".join( re.split(r'\s+', raw.strip())[0:10] )
                html += '<p class="feed-content">%s&nbsp;<a href="%s">...</a></p>'%( trimmed, item.link )
        return html
    
