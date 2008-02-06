from ScriptingBridge import *
from Extractor import *
from Utilities import *

class ComRancheroNetNewsWire(Extractor):

    def __init__(self):
        super( ComRancheroNetNewsWire, self ).__init__()
        self.nnw = SBApplication.applicationWithBundleIdentifier_("com.ranchero.NetNewsWire")

    def clues(self):
        selected = self.nnw.selectedHeadline()
        if not selected.exists(): return

        if selected.objectDescription():
            self.clues_from_microformats( selected.objectDescription() )
        self.clues_from_url( selected.URL() )
        self.clues_from_url( selected.subscription().homeURL() )
