from FeedProvider import *

# cunning subclassing of feedprovider here as a demo.
class TwitterProvider( FeedProvider ):

    def provide( self ):
        self.username = NSUserDefaults.standardUserDefaults().stringForKey_("twitterUsername")
        self.password = NSUserDefaults.standardUserDefaults().stringForKey_("twitterPassword")
        # grab the urls for us - this stops the feedParser from looking for
        # RSS/atom feeds in these urls. Have to do this _here_, rather
        # than in run, so we get them before feedParser has a chance
        self.urls = self.person.takeUrls(r'twitter\.com/.')

        # do we have anything to do?
        if self.urls: self.start()
    
    def guardedRun(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        
        self.atoms = [ "<h3><a href='http://twitter.com/%s'>Twitter</a>&nbsp;<img src='spinner.gif'></h3>"%self.username ]
        self.changed()

        # deriving the feed url from the username is faster than
        # fetching the HTML first.
        username = re.search(r'twitter\.com/([^/]+)', self.urls[0]).group(1)
        auth = ""
        if self.username and self.password:
            # TODO - escape
            auth = "%s:%s@"%( self.username, self.password )
            
        feed = self.getFeed( self.urls[0], "http://%stwitter.com/statuses/user_timeline/%s.atom"%( auth, username ) )
        if not feed or not feed.entries:
            self.atoms = []
            self.changed
            return
        
        tweet = feed.entries[0].title

        self.atoms = [ "<h3><a href='http://twitter.com/%s'>Twitter</a></h3>"%self.username, "<p>%s</p>"%tweet ]
        self.changed()
        