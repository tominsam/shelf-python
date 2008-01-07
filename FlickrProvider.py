from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLink

class FlickrProvider( Provider ):
    cache = {}

    def provide( self ):
        flickrs = self.person.takeUrls(r'flickr\.com/(photos|person)/.')
        if flickrs:
            self.username = re.search(r'/(photos|person)/([^/]+)', flickrs[0]).group(2)
            self.start()

    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        

        self.atoms = [ "<h3><a href='http://flickr.com/photos/%s'>Flickr</a>&nbsp;<img src='spinner.gif'></h3>"%self.username, "<p>" ]
        self.changed()
        
        if not self.username in FlickrProvider.cache:
            url = "http://flickr.com/photos/%s"%self.username
            rss = getRSSLink( url )
            feed = feedparser.parse( rss )
            FlickrProvider.cache[ self.username ] = feed
        
        entries = FlickrProvider.cache[ self.username ].entries
        for item in entries[0:4]:
            img = item.enclosures[0].href
            img = re.sub(r'_m.jpg', '_s.jpg', img)
            self.atoms.append("<a href='%s'><img src='%s' width='32' height='32' style='margin: 3px'></a>"%( item.link, img ) )
        
        self.atoms[0] = "<h3><a href='http://flickr.com/photos/%s'>Flickr</a></h3>"%self.username
        self.atoms.append("</p>")
        self.changed()
