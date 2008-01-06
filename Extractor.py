from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

import re
from email.utils import parseaddr

class Extractor(object):

    def __init__(self):
        NSLog("** %s init"%self.__class__.__name__)
        super( Extractor, self ).__init__()
        self.addressBook = ABAddressBook.sharedAddressBook()

    def clues_from_email( self, email ):
        # email look like 'Name <email>' sometimes.
        name, email = parseaddr( email )
        print("Looking for people with email '%s'"%email)
        return self._search_for( email, "Email" )
    
    def clues_from_url( self, url ):
        if not url: return []
        print("Looking for people with url '%s'"%url)
        clues = self._search_for( url, "URLs" ) + self._search_for( url + "/", "URLs" ) 
        while len(clues) == 0 and re.search(r'//.*?/', url):
            url = re.sub(r'/[^/]*$','',url)
            print("Looking for people with url '%s'"%url)
            clues = self._search_for( url, "URLs" ) + self._search_for( url + "/", "URLs" ) 
        return clues

    def clues_from_aim( self, aim ):
        print("Looking for people with AIM %s"%aim)
        return self._search_for( aim, "AIMInstant" )
    
    def clues_from_name( self, name ):
        names = re.split(r'\s+', name)
        return self.clues_from_names( names[0], names[-1] )

    def clues_from_names( self, forename, surname ):
        print("Looking for people called '%s' '%s'"%( forename, surname ))
        forename_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABFirstNameProperty, None, None, forename, kABPrefixMatchCaseInsensitive )
        surname_search = ABPerson.searchElementForProperty_label_key_value_comparison_( kABLastNameProperty, None, None, surname, kABEqualCaseInsensitive )
        se = ABSearchElement.searchElementForConjunction_children_( kABSearchAnd, [ forename_search, surname_search ] )
        return list(self.addressBook.recordsMatchingSearchElement_( se ))
        
    
    def _search_for( self, thing, type ):
        if not thing or len(thing) == 0:
            return []
            
        se = ABPerson.searchElementForProperty_label_key_value_comparison_( type, None, None, thing, kABEqualCaseInsensitive )
        return list(self.addressBook.recordsMatchingSearchElement_( se ))
