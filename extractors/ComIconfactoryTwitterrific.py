from ScriptingBridge import *
from Extractor import *
from Utilities import _info

class ComIconfactoryTwitterrific(Extractor):

    def __init__(self):
        super( ComIconfactoryTwitterrific, self ).__init__()
        self.twitterific = SBApplication.applicationWithBundleIdentifier_("com.iconfactory.Twitterrific")

    def clues(self):
        if not self.twitterific.tweets().count(): return

        url = self.twitterific.selection().userUrl()
        self.clues_from_url( url )

        username = self.twitterific.selection().screenName()
        self.clues_from_url("http://twitter.com/%s"%( username ) )
