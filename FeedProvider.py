from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLink

class FeedProvider( Provider ):

    def provide( self ):
        self.atoms = [ "<h3>Looking for RSS feeds&nbsp;<img src='spinner.gif'></h3>" ]
        self.start()
    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        
        self.atoms = []

        for url in self.person.boring_urls:
            if not self.running: return

            print("Looking at %s for feed"%url)
            self.atoms.append("<h3>%s&nbsp;<img src='spinner.gif'></h3>"%url)
            self.changed()

            rss = getRSSLink( url )
            if rss:
                if not self.running: return

                print("Found feed url %s"%( rss ))

                feed = feedparser.parse( rss )
                if feed['feed']:
                    print( "Parsed feed" )
                    html = "<h3>%s</h3>"%feed['feed']['title']
                    entries = feed.entries
                    for item in entries[0:4]:
                        html += '<p><a href="%s">%s</a></p>'%( item.link, item.title )
                    self.atoms[-1] = html
                    self.changed()
                else:
                    print(" Can't parse feed" )
                    self.atoms = self.atoms[:-1]
            else:
                print("No feed" )
                self.atoms = self.atoms[:-1]
        
        self.changed()


Provider.PROVIDERS.append( FeedProvider )