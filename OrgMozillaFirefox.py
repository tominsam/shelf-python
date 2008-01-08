from Extractor import *
from AppKit import *

class OrgMozillaFirefox( Extractor ):

    def __init__(self):
        super( OrgMozillaFirefox, self ).__init__()

    def clues(self):
        # thanks, mark
        script = """
            tell application "Firefox"
                set myFirefox to properties of front window as list
                get item 3 of myFirefox
            end tell
        """

        ascript = NSAppleScript.alloc().initWithSource_( script )
        [ ret, error ] = ascript.executeAndReturnError_()
        url = ret.stringValue()
        return self.clues_from_url( url )
