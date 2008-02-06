from Foundation import *
from AppKit import *

# based on example at http://svn.red-bean.com/pyobjc/trunk/pyobjc/pyobjc-framework-Cocoa/Examples/AppKit/HotKeyPython/

from Carbon.CarbonEvt import RegisterEventHotKey, GetApplicationEventTarget
from Carbon.Events import cmdKey, controlKey

kEventHotKeyPressedSubtype = 6
kEventHotKeyReleasedSubtype = 9

class PyShelfApplication(NSApplication):

    def finishLaunching(self):
        super(PyShelfApplication, self).finishLaunching()
        # register cmd-control-J
        self.hotKeyRef = RegisterEventHotKey(38, cmdKey | controlKey, (0, 0), GetApplicationEventTarget(), 0)

    def sendEvent_(self, theEvent):
        if theEvent.type() == NSSystemDefined and theEvent.subtype() == kEventHotKeyPressedSubtype:
            self.activateIgnoringOtherApps_(True)
            NSRunAlertPanel(u'Hot Key Pressed', u'Hot Key Pressed',
                None, None, None)
        super(PyShelfApplication, self).sendEvent_(theEvent)

