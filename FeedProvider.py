from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLinkFromHTMLSource

class FeedProvider( Provider ):

    def provide( self ):
        self.atoms = []
        self.start()
    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        

        self.atoms = [ "<h3><a href='%s'>%s</a></h3>"%(url,url) for url in self.person.boring_urls ]

        index = 0
        for url in self.person.boring_urls:

            print("Looking at %s for feed"%url)
            self.atoms[ index ] = "<h3><a href='%s'>%s</a>&nbsp;<img src='spinner.gif'></h3>"%(url,url)
            
            feed = self.getFeed( url )
            if feed:
                html = "<h3><a href='%s'>%s</a></h3>"%( url, feed['feed']['title'] )
                entries = feed.entries
                for item in entries[0:4]:
                    html += '<p><a href="%s">%s</a></p>'%( item.link, item.title )
                self.atoms[ index ] = html
                index += 1
            else:
                self.atoms[ index : index + 1 ] = []
        
            self.changed()
    
    def getFeed( self, url, rss = None ):
        if not rss:
            rss = getRSSLinkFromHTMLSource( self.cacheUrl( url ) )
        
        if rss:
            feed = feedparser.parse( self.cacheUrl( rss ) )
            if feed and 'feed' in feed:
                return feed

