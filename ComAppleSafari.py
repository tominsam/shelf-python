from ScriptingBridge import *
from Extractor import *

class ComAppleSafari(Extractor):

    def __init__(self):
        super( ComAppleSafari, self ).__init__()
        self.safari = SBApplication.applicationWithBundleIdentifier_("com.apple.safari")

    def clues(self):
        clues = []

        # window 0 is always the foreground window?
        url = self.safari.windows()[ 0 ].currentTab().URL()
        NSLog(" - current url is %s"%url)
        clues += self.clues_from_url( url )

        # TODO - look for embedded vcard?

        return clues
