from ScriptingBridge import *
from Extractor import *
from Utilities import *

class ComAppleIChat(Extractor):

    def __init__(self):
        super( ComAppleIChat, self ).__init__()
        self.ichat = SBApplication.applicationWithBundleIdentifier_("com.apple.iChat")

    def clues(self):
        if self.ichat.chats().count() == 0: return []
        # iChat sucks. There's no 'active Chat' variable, so I'm going to
        # (a) Guess based on the window name, looking for a name, then
        # (b) Just use the first element of the chats() array. Which is the
        # first opened chat. TODO - I can do better - use the most recently updated
        # chat. Not _much_ better...
        username = None
        title = self.ichat.windows()[0].name()
        match = re.search(r'Chat with (.*)', title) # probably won't work with localization
        if match:
            name = match.group(1)
            chats = filter(lambda c: c.participants()[0].fullName() == name, self.ichat.chats())
            if chats:
                username = chats[0].participants()[0].handle()
                
        # give up, use first chat.
        if not username:
            username = self.ichat.chats()[0].participants()[0].handle()

        if username:
            self.clues_from_aim( username )
            self.clues_from_jabber( username )
