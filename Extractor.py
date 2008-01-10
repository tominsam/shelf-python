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

from Clue import *

class Extractor(object):

    def __init__(self):
        #NSLog("** Extractor '%s' init"%self.__class__.__name__)
        super( Extractor, self ).__init__()
        self.addressBook = ABAddressBook.sharedAddressBook()

    def clues_from_email( self, email ):
        # email look like 'Name <email>' sometimes.
        name, email = parseaddr( email )
        #print("Looking for people with email '%s'"%email)
        return self._search_for( email, "Email" )
    
    def clues_from_url( self, url ):
        if not url: return []
        url = re.sub(r'^\w+://(www\.)?','',url)
        #print("Looking for people with url '%s'"%url)
        clues = self._search_for( url, "URLs", kABSuffixMatchCaseInsensitive ) + self._search_for( url + "/", "URLs", kABSuffixMatchCaseInsensitive )
        while len(clues) == 0 and re.search(r'/', url):
            url = re.sub(r'/[^/]*$','',url)
            #print("Looking for people with url '%s'"%url)
            clues = self._search_for( url, "URLs", kABSuffixMatchCaseInsensitive ) + self._search_for( url + "/", "URLs", kABSuffixMatchCaseInsensitive )
        return clues

    def clues_from_aim( self, username ):
        #print("Looking for people with AIM %s"%username)
        return self._search_for( username, kABAIMInstantProperty )
    
    def clues_from_jabber( self, username ):
        #print("Looking for people with Jabber %s"%username)
        return self._search_for( username, kABJabberInstantProperty )
    
    def clues_from_yahoo( self, username ):
        #print("Looking for people with Yahoo! %s"%username)
        return self._search_for( username, kABYahooInstantProperty )
    
    def clues_from_name( self, name ):
        names = re.split(r'\s+', name)
        return self.clues_from_names( names[0], names[-1] )

    def clues_from_names( self, forename, surname ):
        #print("Looking for people called '%s' '%s'"%( forename, surname ))
        forename_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABFirstNameProperty, None, None, forename, kABPrefixMatchCaseInsensitive )
        surname_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABLastNameProperty, None, None, surname, kABEqualCaseInsensitive )
        se = ABSearchElement.searchElementForConjunction_children_( kABSearchAnd, [ forename_search, surname_search ] )
        return map(lambda a: Clue(a), self.addressBook.recordsMatchingSearchElement_( se ))
        
    
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
            print "Can't get anything useful from %s"%(repr(card))
        
        return clues

