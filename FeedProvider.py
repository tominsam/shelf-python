from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLinkFromHTMLSource
import urllib, urlparse

class FeedProvider( Provider ):

    def provide( self ):
        self.atoms = []
        self.start()
    
    def guardedRun(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        

        todo = self.person.boring_urls
        done = []
        
        def tick( doing = None ):
            self.atoms = done + [ "<h3><a href='%s'>%s</a></h3>"%(url,url) for url in todo ]
            if doing: self.atoms[0:0] = [ doing ]
            self.changed()

        tick()

        while todo:
            url = todo[0]
            todo = todo[1:]
            
            print("Looking at %s for feed"%url)
            tick("<h3><a href='%s'>%s</a>&nbsp;<img src='spinner.gif'></h3>"%(url,url))
            
            feed = self.getFeed( url )
            if feed:
                html = "<h3><a href='%s'>%s</a></h3>"%( url, feed.feed.title )
                entries = feed.entries
                for item in entries[0:4]:
                    html += '<p><a href="%s">%s</a></p>'%( item.link, item.title )
                done.append(html)

            tick()
        
    def getFeed( self, url, rss = None ):
        if not rss:
            rss = getRSSLinkFromHTMLSource( self.cacheUrl( url ) )
            rss = urlparse.urljoin( url, rss )
        
        if rss:
            feed = feedparser.parse( self.cacheUrl( rss ) )
            if feed and 'feed' in feed and 'title' in feed.feed:
                return feed

        return None

