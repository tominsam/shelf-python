from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

import re
from email.utils import parseaddr
import microformatparser
import sgmllib
from HTMLParser import HTMLParseError
import urllib, urlparse, urllib2
from urllib import quote
import simplejson

import Cache
from Utilities import _info
from Clue import *

class Extractor(object):

    def __init__(self):
        #NSLog("** Extractor '%s' init"%self.__class__.__name__)
        super( Extractor, self ).__init__()
        self.addressBook = ABAddressBook.sharedAddressBook()
        
    def getClue( self, caller ):
        NSObject.cancelPreviousPerformRequestsWithTarget_( self )
        self.caller = caller
        self.clues() # implemented in subclasses. Calls addClues

    def addClues( self, clues ):
        if clues and self.caller:
            _info("found a clue!")
            self.caller.gotClue( clues[0] )
            self.caller = None
            NSObject.cancelPreviousPerformRequestsWithTarget_( self )

    def clues_from_email( self, email ):
        # email look like 'Name <email>' sometimes.
        name, email = parseaddr( email )
        _info("Looking for people with email '%s'"%email)
        self.addClues( self._search_for( email, "Email" ) )
    
    def clues_from_url( self, url ):
        if not url: return
        original = url # preserve
        
        clues = self._search_for_url( url )

        while not clues and re.search(r'/', url):
            url = re.sub(r'/[^/]*$','',url)
            clues += self._search_for_url( url )

        if not clues:
            graph_urls = self.getSocialGraphFor( original )

        self.addClues( clues )
    
    def _search_for_url( self, url ):
        url = re.sub(r'^\w+://(www\.)?','',url) # strip leanding http:// and www (if present)
        url = re.sub(r'/+$', '', url) # strip trailing slash
        
        _info("Looking for people with URL '%s'"%url)

        # search for url, plus url with trailing slash
        clues =  self._search_for( url, "URLs", kABSuffixMatchCaseInsensitive )
        clues += self._search_for( url + "/", "URLs", kABSuffixMatchCaseInsensitive )
        return clues

    def clues_from_aim( self, username ):
        _info("Looking for people with AIM %s"%username)
        self.addClues( self._search_for( username, kABAIMInstantProperty ) )
    
    def clues_from_jabber( self, username ):
        _info("Looking for people with Jabber %s"%username)
        self.addClues( self._search_for( username, kABJabberInstantProperty ) )
    
    def clues_from_yahoo( self, username ):
        _info("Looking for people with Yahoo! %s"%username)
        self.addClues( self._search_for( username, kABYahooInstantProperty ) )
    
    def clues_from_name( self, name ):
        names = re.split(r'\s+', name)
        self.addClues( self.clues_from_names( names[0], names[-1] ) )

    def clues_from_names( self, forename, surname ):
        _info("Looking for people called '%s' '%s'"%( forename, surname ))
        forename_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABFirstNameProperty, None, None, forename, kABPrefixMatchCaseInsensitive )
        surname_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABLastNameProperty, None, None, surname, kABEqualCaseInsensitive )
        se = ABSearchElement.searchElementForConjunction_children_( kABSearchAnd, [ forename_search, surname_search ] )
        self.addClues( map(lambda a: Clue(a), self.addressBook.recordsMatchingSearchElement_( se )) )
        
    
    def _search_for( self, thing, type, method = kABEqualCaseInsensitive ):
        if not thing or len(thing) == 0:
            return []
            
        se = ABPerson.searchElementForProperty_label_key_value_comparison_( type, None, None, thing, method )
        return map(lambda a: Clue(a), self.addressBook.recordsMatchingSearchElement_( se ))


    def clues_from_microformats( self, source ):
        try:
            feeds = microformatparser.parse( source )
        except HTMLParseError:
            return []
        
        if not feeds: return []

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
            clues += self.clues_from_url( card['url'] )

        if 'email' in card:
            if isinstance(card['email'], str) or isinstance(card['email'], unicode):
                addrs = [ card['email'] ]
            else:
                addrs = [ e[1] for e in card['email'] ]
                
            for addr in addrs:
                # bloody flickr
                e = re.sub(r'\s*\[\s*at\s*\]\s*', '@', addr)
                clues += self.clues_from_email( e )

        if 'family-name' in card and 'given-name' in card:
            # TODO - check ordering here for .jp issues? Gah.
            clues += self.clues_from_names( card['given-name'], card['family-name'] )
        
        if 'fn' in card:
             clues += self.clues_from_name( card['fn'] )

        if len(clues) == 0:
            _info( "Can't get anything useful from %s"%(repr(card)) )
        
        self.addClues( clues )

    def getSocialGraphFor( self, url ):
        api = "http://socialgraph.apis.google.com/lookup?pretty=1&fme=1"
        api += "&q=" + quote( url )
        _info("Social graph API call to " + api )
        Cache.getContentOfUrlAndCallback( self.gotSocialGraphData, api )
    
    def gotSocialGraphData( self, raw ):
        print("got %s"%raw)
        data = simplejson.loads( raw )
        urls = data['nodes'].keys()
        extra = []
        for u in urls:
            if 'unverified_claiming_nodes' in data['nodes'][u]:
                extra += data['nodes'][u]['unverified_claiming_nodes']
        urls += extra # TODO _ weed dupes

        for graph_url in urls:
            _info("Looking for people with url (from social graph) '%s'"%graph_url)
            self.addClues( self._search_for_url( graph_url ) )

