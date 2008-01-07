from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLink

class FeedProvider( Provider ):

    def provide( self ):
        self.atoms = [ "<h3>Looking for RSS feeds</h3>" ]
        self.start()
    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        

        urls = self.person.urls()
        for url in urls:
            print("Looking at %s for feed"%url)
            self.atoms.append("<p>&raquo; %s <img src='spinner.gif'></p>"%url)
            self.changed()

            rss = getRSSLink( url )
            if rss:
                print("Found feed url %s"%( rss ))
                self.atoms[-1] = "<p>&raquo; %s <img src='spinner.gif'></p>"%rss
                self.changed()

                feed = feedparser.parse( rss )
                if feed['feed']:
                    print( "Parsed feed as %s"%feed['feed']['title'] )
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
        
        self.atoms = self.atoms[1:] # strip the 'looking..'
        self.changed()


Provider.PROVIDERS.append( FeedProvider )