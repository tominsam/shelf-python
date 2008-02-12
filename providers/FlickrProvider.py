from FeedProvider import *
from Utilities import *

class FlickrAtom( FeedAtom ):

    def htmlForFeed( self, url, feed, stale = False ):
        html = ""

        entries = feed.entries
        for item in entries[0:4]:

            date = None
            if 'published_parsed' in item: date = item.published_parsed
            elif 'updated_parsed' in item: date = item.updated_parsed
            if date:
                #html += u'<span class="feed-date">%s</span>'%( time.strftime("%b %d", date ) )
                ago = time_ago_in_words(date) + " ago"
                html += u'<span class="feed-date">%s</span>'%ago

            # ewwwwww
            img = re.search(r'"(http://[^"]*_m.jpg)"', item.content[0].value).group(1)
            img = re.sub(r'_m.jpg', '_t.jpg', img)
            html += "<a href='%s'><img src='%s' class='flickr-image'></a>"%( item.link, img )
            html += '<p class="feed-title"><a href="%s">%s</a></p>'%( item.link, item.title )

            if 'content' in item and len(item.content) > 0:
                detail = item.content[0].value
            elif 'summary' in item and len(item.summary) > 0:
                detail = item.summary
            if detail:
                raw = re.sub(r'<.*?>', '', detail) # strip tags
                try:
                    trimmed = u" ".join( re.split(r'\s+', raw.strip())[0:10] )
                except UnicodeDecodeError:
                    trimmed = u"invalid unicode content"
                html += u'<p class="feed-content">%s&nbsp;<a href="%s">...</a></p>'%( trimmed, item.link )

            html += '<div style="clear:both"></div>'

        return html

class FlickrProvider( FeedProvider ):

    def atomClass(self):
        return FlickrAtom

    def urls(self):
        return self.person.takeUrls(r'flickr\.com/(photos|people)/.')
        
