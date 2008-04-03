from ScriptingBridge import *
from Extractor import *
from Utilities import *

class ComIconfactoryTwitterrific(Extractor):

    def __init__(self):
        super( ComIconfactoryTwitterrific, self ).__init__()
        self.twitterific = SBApplication.applicationWithBundleIdentifier_("com.iconfactory.Twitterrific")

    def clues(self):
        try:
            if not self.twitterific.tweets().count(): return
        except AttributeError:
            # old twitteriffic
            return

        url = self.twitterific.selection().userUrl()
        self.clues_from_url( url )
        if self.done: return

        username = self.twitterific.selection().screenName()
        self.clues_from_url("http://twitter.com/%s"%( username ) )
