from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLink

class FlickrProvider( Provider ):

    def provide( self ):
        flickrs = self.person.takeUrls(r'flickr\.com/(photos|person)/.')
        if flickrs:
            self.username = re.search(r'/(photos|person)/([^/]+)', flickrs[0]).group(2)
            self.start()

    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        

        self.atoms = [ "<h3>Flickr&nbsp;<img src='spinner.gif'></h3>", "<p>" ]
        self.changed()

        url = "http://flickr.com/photos/%s"%self.username
        rss = getRSSLink( url )
        feed = feedparser.parse( rss )
        entries = feed.entries
        for item in entries[0:4]:
            img = item.enclosures[0].href
            img = re.sub(r'_m.jpg', '_s.jpg', img)
            self.atoms.append("<a href='%s'><img src='%s' width='32' height='32' style='margin: 3px'></a>"%( item.link, img ) )
        
        self.atoms[0] = "<h3>Flickr</h3>"
        self.atoms.append("</p>")
        self.changed()
    
Provider.PROVIDERS.append( FlickrProvider )
