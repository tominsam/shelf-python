from ScriptingBridge import *
from Extractor import *

class ComAppleIChat(Extractor):

    def __init__(self):
        super( ComAppleIChat, self ).__init__()
        self.ichat = SBApplication.applicationWithBundleIdentifier_("com.apple.iChat")

    def clues(self):
        if self.ichat.chats().count() == 0: return []
        # THIS IS WRONG
        username = self.ichat.chats()[0].participants()[0].handle()
        return self.clues_from_aim( username ) + self.clues_from_jabber( username )
