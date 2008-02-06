from ScriptingBridge import *
from Extractor import *
from AddressBook import *
from Utilities import *

class ComAppleAddressBook( Extractor ):

    def __init__(self):
        super( ComAppleAddressBook, self ).__init__()
        self.ab = SBApplication.applicationWithBundleIdentifier_("com.apple.AddressBook")

    def clues(self):
        selection = self.ab.selection()
        if selection.count() == 0: return []

        selected_id = selection[0].id()
        
        person = self.addressBook.recordForUniqueId_( selected_id )
        self.addClues( [ Clue.forPerson( person ) ] )
