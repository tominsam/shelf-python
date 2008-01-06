#
#  PyShelfAppDelegate.py
#  PyShelf
#
#  Created by Tom Insam on 06/01/2008.
#  Copyright __MyCompanyName__ 2008. All rights reserved.
#

from Foundation import *
from AppKit import *
from WebKit import *

import PyShelfWindowController

class PyShelfAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
