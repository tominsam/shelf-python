from FeedProvider import *
from Utilities import *

class LastFmAtom( FeedAtom ):

    def htmlForFeed( self, url, feed, stale = False ):
        self.name = "Last.FM"
        
        html = ""

        entries = feed.entries
        for item in entries[0:2]:
            # ewwwwww
            splitted = item.title.split(u"\u2013")
            if len(splitted) != 2:
                return
                
            artist, title = splitted

            date = None
            if 'published_parsed' in item: date = item.published_parsed
            elif 'updated_parsed' in item: date = item.updated_parsed
            
            if date:
                ago = time_ago_in_words(date) + " ago"
                html += u'<span class="feed-date">%s</span>'%ago

            html += "<a href='%s'><img src='%s' class='flickr-image'></a>"%( item.link, "" )

            html += '<p class="feed-title"><a href="%s">%s</a></p>'%( item.link, title )
            html += u'<p class="feed-content">%s</p>'%( artist )

            html += '<div style="clear:both"></div>'

        return html


    def timeout(self):
        return 180

class LastFmProvider( FeedProvider ):

    def atomClass(self):
        return LastFmAtom

    def urls(self):
        return self.person.takeUrls(r'last\.fm/user/.')
    
        
