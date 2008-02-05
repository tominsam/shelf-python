from FeedProvider import *
from Utilities import _info

# cunning subclassing of feedprovider here as a demo.


class TwitterAtom( FeedAtom ):

    def getFeedUrl(self):
        # deriving the feed url from the username is faster than
        # fetching the HTML first.
        username = re.search(r'twitter\.com/([^/]+)', self.url).group(1)
        feed_url = "http://twitter.com/statuses/user_timeline/%s.atom"%(username)
        self.getFeed(
            feed_url,
            NSUserDefaults.standardUserDefaults().stringForKey_("twitterUsername"),
            NSUserDefaults.standardUserDefaults().stringForKey_("twitterPassword")
        )
        

    def htmlForFeed( self, url, feed, stale = False ):
        return '<p>%s</p>'%( feed.entries[0].title )

    def timeout(self):
        return 180
    
class TwitterProvider( FeedProvider ):

    def atomClass(self):
        return TwitterAtom

    def urls(self):
        return self.person.takeUrls(r'twitter\.com/.')
        
