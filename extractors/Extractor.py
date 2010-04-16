from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

import re
from email.utils import parseaddr
import microformatparser
import relmeparser
import sgmllib
from HTMLParser import HTMLParseError
import urllib, urlparse, urllib2
from urllib import quote
import json

import Cache
from Utilities import *
from Clue import *

class Extractor(object):

    def __init__(self):
        #NSLog("** Extractor '%s' init"%self.__class__.__name__)
        super( Extractor, self ).__init__()
        self.addressBook = ABAddressBook.sharedAddressBook()
        
    def getClue( self, caller ):
        self.done = False
        NSObject.cancelPreviousPerformRequestsWithTarget_( self )
        self.caller = caller
        self.clues() # implemented in subclasses. Calls addClues

    def addClues( self, clues, more_urls = [] ):
        print_info("addClues: %s %s" % (str(clues), str(more_urls)))
        if clues and self.caller:
            print_info("found a clue!")
            clues[0].addExtraUrls( more_urls )
            self.caller.gotClue( clues[0] )
            self.caller = None
            self.done = True
            NSObject.cancelPreviousPerformRequestsWithTarget_( self )

    def clues_from_email( self, email, more_urls = [] ):
        if self.done: return
        # email look like 'Name <email>' sometimes.
        name, email = parseaddr( email )
        print_info("Looking for people with email '%s'"%email)
        self.addClues( self._search_for( email, "Email" ), more_urls )
    
    def clues_from_url( self, url, more_urls = [] ):
        if not url: return
        if self.done: return
        original = url # preserve
        
        if re.match(r'xmpp:', url):
            self.clues_from_jabber( re.sub(r'xmpp:', '', url) )
            return

        if re.match(r'email:', url):
            self.clues_from_email( re.sub(r'email:', '', url) )
            return
        
        if re.match(r'\w+:', url) and not re.match(r'http', url):
            # has a protocol, but isn't http
            return
        
        clues = self._search_for_url( url )

        while not clues and re.search(r'//', url):
            url = re.sub(r'/[^/]*$','',url)
            clues += self._search_for_url( url )

        if clues:
            self.addClues( clues, more_urls )

        elif NSUserDefaults.standardUserDefaults().boolForKey_("googleSocial"):
            # this is a background process, calls us back later
            # order is a little sensitive for now, as if the cache is good,
            # the clues are updated _Before_ this function returns.
            # I consider this a bug in the implementation.
            self.getSocialGraphFor( original )

    
    def _search_for_url( self, url ):
        url = normalize_url( url )
        
        print_info("Looking for people with URL '%s'"%url)
        
        previous = Clue.forUrl( url )
        if previous: return [ previous ]

        # search for url, plus url with trailing slash
        clues =  self._search_for( url, "URLs", kABSuffixMatchCaseInsensitive )
        clues += self._search_for( url + "/", "URLs", kABSuffixMatchCaseInsensitive )
        return clues

    def clues_from_aim( self, username, more_urls = [] ):
        if self.done: return
        print_info("Looking for people with AIM %s"%username)
        self.addClues( self._search_for( username, kABAIMInstantProperty ), more_urls )
    
    def clues_from_jabber( self, username, more_urls = [] ):
        if self.done: return
        print_info("Looking for people with Jabber %s"%username)
        self.addClues( self._search_for( username, kABJabberInstantProperty ), more_urls )
    
    def clues_from_yahoo( self, username, more_urls = [] ):
        if self.done: return
        print_info("Looking for people with Yahoo! %s"%username)
        self.addClues( self._search_for( username, kABYahooInstantProperty ), more_urls )
    
    def clues_from_name( self, name, more_urls = [] ):
        if self.done: return
        names = re.split(r'\s+', name)
        self.addClues( self.clues_from_names( names[0], names[-1], more_urls ) )

    def clues_from_names( self, forename, surname, more_urls = [] ):
        if self.done: return
        print_info("Looking for people called '%s' '%s'"%( forename, surname ))
        forename_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABFirstNameProperty, None, None, forename, kABPrefixMatchCaseInsensitive )
        surname_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABLastNameProperty, None, None, surname, kABEqualCaseInsensitive )
        se = ABSearchElement.searchElementForConjunction_children_( kABSearchAnd, [ forename_search, surname_search ] )
        self.addClues( map(lambda a: Clue.forPerson(a), self.addressBook.recordsMatchingSearchElement_( se )), more_urls )
        
    
    def _search_for( self, thing, type, method = kABEqualCaseInsensitive ):
        if not thing or len(thing) == 0:
            return []
            
        se = ABPerson.searchElementForProperty_label_key_value_comparison_( type, None, None, thing, method )
        return map(lambda a: Clue.forPerson(a), self.addressBook.recordsMatchingSearchElement_( se ))


    def clues_from_html( self, source, url ):
        if self.done: return
        try:
            feeds = microformatparser.parse( source, url )
        except HTMLParseError:
            feeds = []
        except UnicodeDecodeError:
            feeds = []
        except TypeError:
            feeds = []

        try:
            relmes = relmeparser.parse( source, url )
        except HTMLParseError:
            relmes = []
        except UnicodeDecodeError:
            relmes = []

        # try all rel="me" links for urls we can deal with.
        for relurl in relmes:
            self.clues_from_url( relurl, relmes )
            if self.done: return

        if not feeds: return

        # I'm going to assume that the _first_ microformat on the page
        # is the person the page is about. I can't really do better
        # than that, can I?
        # TODO - yes, I can. Look for 'rel="me"'
        feed = feeds[0]

        # look for vcard microformats
        vcards = [ tree for name, tree in feed if name =='vcard']
        if not vcards: return []

        card = dict(vcards[0])
        clues = []
        
        if 'url' in card:
            self.clues_from_url( card['url'], [url] + relmes )

        if 'email' in card:
            if isinstance(card['email'], str) or isinstance(card['email'], unicode):
                addrs = [ card['email'] ]
            else:
                addrs = [ e[1] for e in card['email'] ]
                
            for addr in addrs:
                # bloody flickr
                e = re.sub(r'\s*\[\s*at\s*\]\s*', '@', addr)
                self.clues_from_email( e, [url] + relmes )

        if 'family-name' in card and 'given-name' in card:
            # TODO - check ordering here for .jp issues? Gah.
            self.clues_from_names( card['given-name'], card['family-name'], [url] + relmes )
        
        if 'fn' in card:
            self.clues_from_name( card['fn'], [url] + relmes )


    SOCIAL_GRAPH_CACHE = {}
    def getSocialGraphFor( self, url, more_urls = [] ):
        if not re.match(r'http', url): return

        if url in Extractor.SOCIAL_GRAPH_CACHE:
            print_info("using cached social graph data")
            self.addClues( Extractor.SOCIAL_GRAPH_CACHE[url], more_urls )
            return
        api = "http://socialgraph.apis.google.com/lookup?pretty=1&fme=1&edo=1&edi=1"
        api += "&q=" + quote( url, '' )
        print_info("Social graph API call to " + api )
        # TODO _ respect more_urls here
        Cache.getContentOfUrlAndCallback( callback = self.gotSocialGraphData, url = api, timeout = 3600 * 48 ) # huge timeout here

    def gotSocialGraphData( self, raw, isStale ):
        try:
            data = json.loads( raw )
        except ValueError:
            return # meh
        original_url = data['canonical_mapping'].keys()[0]
        urls = filter( lambda u: len(u) > 4 and re.match(r'http', u), data['nodes'].keys() ) # sometimes it returns '/' as a node.
        extra = []
        for u in urls:
            if 'unverified_claiming_nodes' in data['nodes'][u]:
                extra += data['nodes'][u]['unverified_claiming_nodes']
        urls += extra # TODO _ weed dupes

        for graph_url in urls:
            print_info("Google Social Graph URL '%s'"%graph_url)
            clues = self._search_for_url( graph_url )
            self.addClues( clues )
            if clues:
                Extractor.SOCIAL_GRAPH_CACHE[ original_url ] = clues
                return # done

        Extractor.SOCIAL_GRAPH_CACHE[ original_url ] = []
