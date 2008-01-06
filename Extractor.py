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
        return self._search_for( email, "Email" )
    
    def clues_from_url( self, url ):
        if not url: return []
        print("Trying url %s"%url)
        clues = self._search_for( url, "URLs" ) + self._search_for( url + "/", "URLs" ) 
        while len(clues) == 0 and re.search(r'//.*?/', url):
            url = re.sub(r'/[^/]*$','',url)
            print("Trying url %s"%url)
            clues = self._search_for( url, "URLs" ) + self._search_for( url + "/", "URLs" ) 
        return clues

    def clues_from_aim( self, url ):
        return self._search_for( url, "AIMInstant" )
    
    def _search_for( self, thing, type ):
        if not thing or len(thing) == 0:
            return []
            
        se = ABPerson.searchElementForProperty_label_key_value_comparison_( type, None, None, thing, kABEqual )
        return list(self.addressBook.recordsMatchingSearchElement_( se ))
