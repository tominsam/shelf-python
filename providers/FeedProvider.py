from Provider import *
from urllib import quote

import feedparser
from autorss import getRSSLinkFromHTMLSource
import urllib, urlparse
import time

from Utilities import *
import Cache

class FeedAtom(ProviderAtom):
    def __init__(self, *stuff):
        ProviderAtom.__init__( self, *stuff )
        self.feed = None
        self.feed_url = None
        self.refresh( False )
    
    def refresh( self, force ):
        # TODO - force-refresh should blow the cache
        self.getFeedUrl()
    
    def sortOrder(self):
        if not self.feed:
            return MIN_SORT_ORDER
        if len(self.feed.entries) == 0:
            return MIN_SORT_ORDER
        if 'updated_parsed' in self.feed.entries[0] and self.feed.entries[0].updated_parsed:
            return time.mktime(self.feed.entries[0].updated_parsed)
        if "published_parsed" in self.feed.entries[0] and self.feed.entries[0].published_parsed:
            return time.mktime(self.feed.entries[0].published_parsed)
        return MIN_SORT_ORDER
    
    def getFeedUrl(self):
        # it's very unlikely that the feed source will move
        # TODO - check stale cache first. Man, the feed provider is too complicated.
        special = self.specialCaseFeedUrl( self.url )
        # return None to mean 'no special case', blank string to mean "no feed here"
        if special != None:
            if len(special) > 0:
                print_info("special-case feed url %s"%special)
                self.getFeed( special )
            else:
                # bad feed
                self.dead = True
                self.changed()
            return
    
        Cache.getContentOfUrlAndCallback( callback = self.gotMainPage, url = self.url, timeout = self.timeout() * 10, wantStale = False, failure = self.failed ) # TODO - use stale version somehow
    
    def specialCaseFeedUrl( self, url ):
        print_info("trying to special-case url %s"%url)
        if re.match(r'http://search\.cpan\.org/~', url):
            print_info("RSS feed is known-bad (search.cpan)")
            return "" # bad feed
        if re.match(r'http://use\.perl\.org/~\w+/?$', url): # /journal is ok
            print_info("RSS feed is known-bad (use.perl)")
            return "" # bad feed
        
        print_info("No special case")
        return None

    def gotMainPage( self, data, stale ):
        rss = getRSSLinkFromHTMLSource(data)
        if rss:
            feed_url = urlparse.urljoin( self.url, rss )
            self.getFeed( feed_url )
        else:
            self.dead = True
            self.changed()
    
    def username(self): return None
    def password(self): return None
    
    def getFeed(self, feed_url ):
        if not self.feed_url and self.provider.isDuplicateFeed( feed_url ):
            self.dead = True
            self.changed()
        else:
            self.feed_url = feed_url
            # if we have a feed object, then I'm not interested in re-parsing a stale file.
            wantStale = not self.feed
            Cache.getContentOfUrlAndCallback( callback = self.gotFeed, url = feed_url, username = self.username(), password = self.password(), timeout = self.timeout(), wantStale = wantStale, failure = self.failed )

    def gotFeed( self, data, stale ):
        feed = feedparser.parse( data )
        if feed and 'feed' in feed and 'title' in feed.feed:
            self.feed = feed
            self.stale = stale
            self.name = feed.feed.title
            self.changed()
        else:
            self.dead = True
            self.changed()
        
    def failed( self, error ):
        if self.feed:
            # never mind, we have _something_
            self.stale = False
        else:
            # no old feed, just display error
            self.error = error
            self.stale = False
        self.changed()

    def body(self):
        if self.feed and self.feed.entries:
            return self.htmlForFeed( url = self.url, feed = self.feed, stale = self.stale )
        elif self.feed:
            return "" # no entries
        else:
            return self.htmlForPending( url = self.url, stale = self.stale )

    def timeout(self):
        return 60 * 20

    def htmlForPending( self, url, stale = False ):
        return ""
    
    def htmlForFeed( self, url, feed, stale = False ):
        html = u""
        entries = feed.entries
        for item in filter( lambda item: "link" in item, entries )[0:4]:
            if 'published_parsed' in item: date = item.published_parsed
            elif 'updated_parsed' in item: date = item.updated_parsed
            else: date = None
            
            if date:
                #html += u'<span class="feed-date">%s</span>'%( time.strftime("%b %d", date ) )
                ago = time_ago_in_words(date) + " ago"
                html += u'<span class="feed-date">%s</span>'%ago
            title = 'title' in item and item.title or "untitled"

            try:
                html += u'<p class="feed-title"><a href="%s">%s</a></p>'%( item.link, title )
            except UnicodeDecodeError:
                html += u'<p class="feed-title"><a href="%s">invalid unicode title</a></p>'%( item.link )
            detail = None
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
                try:
                    html += u'<p class="feed-content">%s&nbsp;<a href="%s">...</a></p>'%( trimmed, item.link )
                except UnicodeDecodeError:
                    html += u'<p class="feed-content">invalid unicode content</p>'
        return html


class FeedProvider( Provider ):
    
    def atomClass(self):
        return FeedAtom

    def provide( self ):
        todo = self.urls() # if we're claiming from boring_urls, do it first
        
        # sync atoms to urls
        for atom in [x for x in self.atoms]:
            if atom.url in todo:
                todo.remove( atom.url )
                atom.refresh( False )
            else:
                self.atoms.remove(atom)
        
        for url in todo:
            atom = self.atomClass()( self, url )
            atom.guessed = url in self.clue.extra_urls
            self.atoms.append( atom )
    
    def isDuplicateFeed(self, url):
        # called once an atom has a feed url for itself. Rather than
        # removing the atom, just mark it as dead, so that the proide()
        # function above doesn't re-add it
        if not url: return False
        return normalize_url(url) in [ normalize_url(a.feed_url) for a in filter(lambda a: a.feed_url, self.atoms) ]
        
    # override these
    def urls(self):
        return self.clue.boring_urls
    
    
