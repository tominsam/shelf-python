from ScriptingBridge import *
from Extractor import *
from Utilities import _info

class ComAppleMail( Extractor ):

    def __init__(self):
        super( ComAppleMail, self ).__init__()
        # handily, this persists across Mail.app restarts
        self.mail = SBApplication.applicationWithBundleIdentifier_("com.apple.mail")

    def clues(self):
        # are we looking at a message viewer
        if self.mail.windows()[0].id() in map( lambda v: v.window().id(), self.mail.messageViewers() ):
            messages = self.mail.selection()
            if messages.count() > 0:
                return self.clues_from_email( messages[0].sender() )
    
        # composer?
        else:
            return []

