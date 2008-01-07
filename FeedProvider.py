from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLink

class FeedProvider( Provider ):
    cache = {}

    def provide( self ):
        self.atoms = [ "<h3>Looking for RSS feeds&nbsp;<img src='spinner.gif'></h3>" ]
        self.start()
    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        
        self.atoms = []

        for url in self.person.boring_urls:

            print("Looking at %s for feed"%url)
            self.atoms.append("<h3>%s&nbsp;<img src='spinner.gif'></h3>"%url)
            self.changed()
            
            feed = self.getFeed( url )
            if feed:
                html = "<h3>%s</h3>"%feed['feed']['title']
                entries = feed.entries
                for item in entries[0:4]:
                    html += '<p><a href="%s">%s</a></p>'%( item.link, item.title )
                self.atoms[-1] = html
            else:
                self.atoms = self.atoms[:-1]
        
            self.changed()
    
    def getFeed( self, url ):
        if not 'feed' in FeedProvider.cache:
            FeedProvider.cache['feed'] = {}
        if not url in FeedProvider.cache['feed']:
            FeedProvider.cache['feed'][url] = None
            rss = getRSSLink( url )
            if rss:
                feed = feedparser.parse( rss )
                if feed and 'feed' in feed:
                    FeedProvider.cache['feed'][url] = feed
        # TODO - expire cache
        return FeedProvider.cache['feed'][url]



Provider.PROVIDERS.append( FeedProvider )