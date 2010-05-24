from ScriptingBridge import *
from Extractor import *
from Utilities import *

class ComSkypeSkype(Extractor):

    def __init__(self):
        super( ComSkypeSkype, self ).__init__()
        self.skype = SBApplication.applicationWithBundleIdentifier_("com.skype.skype")

    def clues(self):
        # first window is an invisible emoticons tihng
        
        if not self.skype.windows().count() > 1:
            return
        chat = self.skype.windows()[1]
        if not chat.exists(): return []
        
        # seriously, this is the best we can do?
        name = chat.name()
        self.clues_from_name( name )
