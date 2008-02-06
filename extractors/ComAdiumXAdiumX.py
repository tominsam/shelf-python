from ScriptingBridge import *
from Extractor import *
from Utilities import *

class ComAdiumXAdiumX(Extractor):

    def __init__(self):
        super( ComAdiumXAdiumX, self ).__init__()
        self.adium = SBApplication.applicationWithBundleIdentifier_("com.adiumX.adiumX")

    def clues(self):
        chat = self.adium.activeChat()
        if not chat.exists(): return []
        account_type = chat.ID().split(".")[0].lower()
        username = ".".join( chat.ID().split(".")[1:] )
        if account_type in ['aim', 'mac']:
            self.clues_from_aim( username )
        elif account_type in ['jabber', 'gtalk', 'livejournal']:
            self.clues_from_jabber( username )
        elif account_type in ['yahoo!']:
            self.clues_from_yahoo( username )
