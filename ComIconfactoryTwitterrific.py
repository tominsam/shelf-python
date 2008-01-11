from ScriptingBridge import *
from Extractor import *
from Utilities import _info

class ComIconfactoryTwitterrific(Extractor):

    def __init__(self):
        super( ComIconfactoryTwitterrific, self ).__init__()
        self.twitterific = SBApplication.applicationWithBundleIdentifier_("com.iconfactory.Twitterrific")

    def clues(self):
        if self.twitterific.tweets().count() == 0: return []
        url = self.twitterific.selection().userUrl()
        username = self.twitterific.selection().screenName()
        return self.clues_from_url("http://twitter.com/%s"%( username ) ) + self.clues_from_url( url )
