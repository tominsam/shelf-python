from ScriptingBridge import *
from Extractor import *
from AddressBook import *

class ComAppleAddressBook( Extractor ):

    def __init__(self):
        super( ComAppleAddressBook, self ).__init__()
        self.ab = SBApplication.applicationWithBundleIdentifier_("com.apple.AddressBook")

    def clues(self):
        if not self.ab.selection().count() > 0: return []

        selected_id = self.ab.selection()[0].id()
        
        person = ABAddressBook.sharedAddressBook().recordForUniqueId_( selected_id )
        return [ Clue( person ) ]
