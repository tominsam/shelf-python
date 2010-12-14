from FeedProvider import *
from Utilities import *

# cunning subclassing of feedprovider here as a demo.

class TwitterAtom( FeedAtom ):

    def specialCaseFeedUrl( self, url ):
        # deriving the feed url from the username is faster than
        # fetching the HTML first.
        username = re.search(r'twitter\.com/([^/]+)', url).group(1)
        if username == 'home': return ""
        return "http://twitter.com/statuses/user_timeline/%s.atom"%(username)
    
    def username(self):
        return NSUserDefaults.standardUserDefaults().stringForKey_("twitterUsername")
    
    def password(self):
        NSUserDefaults.standardUserDefaults().stringForKey_("twitterPassword")

    def htmlForFeed( self, url, feed, stale = False ):
        item = feed.entries[0]
        html = ""

        date = None
        if 'published_parsed' in item: date = item.published_parsed
        elif 'updated_parsed' in item: date = item.updated_parsed
        if date:
            #html += u'<span class="feed-date">%s</span>'%( time.strftime("%b %d", date ) )
            ago = time_ago_in_words(date) + " ago"
            html += u'<span class="feed-date">%s</span>'%ago
        
        html += '<p>%s</p>'%( item.title )
        return html

    def timeout(self):
        return 180
    
class TwitterProvider( FeedProvider ):

    def atomClass(self):
        return TwitterAtom

    def urls(self):
        return self.clue.takeUrls(r'twitter\.com/.')
        
