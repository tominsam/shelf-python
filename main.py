#
#  main.py
#  PyShelf
#
#  Created by Tom Insam on 06/01/2008.
#  Copyright __MyCompanyName__ 2008. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import PyShelfAppDelegate

# pass control to AppKit
AppHelper.runEventLoop()
