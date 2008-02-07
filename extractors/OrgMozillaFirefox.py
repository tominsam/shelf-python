from Extractor import *
from AppKit import *
from Utilities import *

class OrgMozillaFirefox( Extractor ):

    # Firefox completely refuses to cooperate with the scripting
    # bridge. Annoying as hell.

    def __init__(self):
        super( OrgMozillaFirefox, self ).__init__()

        # thanks, mark
        # DANGER - UTF8 here!
        script = u"""
            tell application "Firefox"
                get \u00ABclass curl\u00BB of front window
            end tell
        """

        self.ascript = NSAppleScript.alloc().initWithSource_( script )

    def clues(self):
        
        [ ret, error ] = self.ascript.executeAndReturnError_( None )
        if error:
            print("ERROR: %s"%repr(error))
            return
        if ret:
            url = ret.stringValue()
            self.clues_from_url( url )
