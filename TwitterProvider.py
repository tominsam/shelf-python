from FeedProvider import *
from Utilities import _info

# cunning subclassing of feedprovider here as a demo.
class TwitterProvider( FeedProvider ):

    def username(self):
        return NSUserDefaults.standardUserDefaults().stringForKey_("twitterUsername")
    
    def password(self):
        return NSUserDefaults.standardUserDefaults().stringForKey_("twitterPassword")
    
    def timeout(self):
        return 180

    def urls(self):
        return self.person.takeUrls(r'twitter\.com/.')
        
    def feed_for_url( self, url ):
        # deriving the feed url from the username is faster than
        # fetching the HTML first.
        username = re.search(r'twitter\.com/([^/]+)', url).group(1)
        return "http://twitter.com/statuses/user_timeline/%s.atom"%(username ), self.username(), self.password()

    def htmlForPending( self, url, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.spinner()
        else:
            spinner_html = ""
        return "<h3><a href='%s'>Twitter</a>%s</h3>"%(url,spinner_html)
    
    def htmlForFeed( self, url, feed, stale = False ):
        if stale:
            spinner_html = "&nbsp;" + self.spinner()
        else:
            spinner_html = ""
        html = "<h3><a href='%s'>Twitter</a>%s</h3>"%( url, spinner_html )
        html += '<p>%s</p>'%( feed.entries[0].title )
        return html
