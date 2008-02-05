from FeedProvider import *
from Utilities import _info

class FlickrAtom( FeedAtom ):

    def htmlForPending( self, url, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.provider.spinner()
        else:
            spinner_html = ""
        return "<h3><a href='%s'>Flickr</a>%s</h3>"%(url,spinner_html)
    
    def htmlForFeed( self, url, feed, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.provider.spinner()
        else:
            spinner_html = ""
        html = "<h3><a href='%s'>Flickr</a>%s</h3>"%( url, spinner_html )

        entries = feed.entries
        for item in entries[0:4]:
            # ewwwwww
            img = re.search(r'"(http://[^"]*_m.jpg)"', item.content[0].value).group(1)
            img = re.sub(r'_m.jpg', '_s.jpg', img)
            html += "<a href='%s'><img src='%s' class='flickr-image'></a>"%( item.link, img )

        return html

class FlickrProvider( FeedProvider ):

    def atomClass(self):
        return FlickrAtom

    def urls(self):
        return self.person.takeUrls(r'flickr\.com/(photos|people)/.')
        
