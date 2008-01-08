from Extractor import *
from AppKit import *

class OrgMozillaFirefox( Extractor ):

    # Firefox completely refuses to cooperate with the scripting
    # bridge. Annoying as hell.

    def __init__(self):
        super( OrgMozillaFirefox, self ).__init__()

        # thanks, mark
        script = """
            tell application "Firefox"
                get «class curl» of front window
            end tell
        """

        self.ascript = NSAppleScript.alloc().initWithSource_( script )

    def clues(self):
        
        [ ret, error ] = self.ascript.executeAndReturnError_()
        url = ret.stringValue()
        return self.clues_from_url( url )
