from FeedProvider import *

class FlickrProvider( FeedProvider ):

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
        
        # TODO - use API!
        feed = self.getFeed( "http://flickr.com/photos/%s"%self.username )
        
        if not feed:
            self.atoms.append("<p>No photos</p>")
            self.changed()
            return
        
        entries = feed.entries
        for item in entries[0:4]:
            img = item.enclosures[0].href
            img = re.sub(r'_m.jpg', '_s.jpg', img)
            self.atoms.append("<a href='%s'><img src='%s' width='40' height='40' style='margin: 3px'></a>"%( item.link, img ) )
        
        self.atoms[0] = "<h3><a href='http://flickr.com/photos/%s'>Flickr</a></h3>"%self.username
        self.atoms.append("</p>")
        self.changed()
