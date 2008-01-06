from ScriptingBridge import *
from Extractor import *

class ComAppleMail( Extractor ):

    def __init__(self):
        super( ComAppleMail, self ).__init__()
        # handily, this persists across Mail.app restarts
        self.mail = SBApplication.applicationWithBundleIdentifier_("com.apple.mail")

    def clues(self):
        clues = []

        messages = self.mail.selection()
        
        for message in messages:
            clues += self.clues_from_email( message.sender() )
        
        return clues

