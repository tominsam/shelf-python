from ScriptingBridge import *
from Extractor import *

class ComAdiumXAdiumX(Extractor):

    def __init__(self):
        super( ComAdiumXAdiumX, self ).__init__()
        self.adium = SBApplication.applicationWithBundleIdentifier_("com.adiumX.adiumX")

    def clues(self):
        if self.adium.AdiumController().chats().count() == 0: return []
        chat = self.adium.AdiumController().chats()[0]
        uid = chat.contact().UID()
        return self.clues_from_aim( uid )
