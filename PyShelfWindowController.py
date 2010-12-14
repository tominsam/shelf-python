from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

from Carbon.AppleEvents import kAEISGetURL, kAEInternetSuite
import struct

import objc
import re
import traceback
import os
from time import time as epoch_time

from Utilities import *
from Clue import *

class ShelfController (NSWindowController):
    companyView = objc.IBOutlet()
    imageView = objc.IBOutlet()
    nameView = objc.IBOutlet()
    webView = objc.IBOutlet()
    prefsWindow = objc.IBOutlet()

    # first-cut init goes here - we've been woken up, and all the GUI
    # component objects exist. Don't spend too long here, though, I think
    # the app icon is still bouncing.
    def awakeFromNib(self):
        self.handlers = {}
        self.current_clue = None

        # get the RGB hex code of the system 'background' color.
        bg = self.window().backgroundColor().colorUsingColorSpaceName_( NSCalibratedRGBColorSpace )
        rgb = "%x%x%x"%(
            bg.redComponent() * 255.999999,
            bg.greenComponent() * 255.999999,
            bg.blueComponent() * 255.999999
        )
        # TODO - ok. Now do something with this information. Specifically, get it into the CSS.
        
        # evil. Alter the webkit view object so that it'll accept a clickthrough
        # - this is very handy, as the window is on top and full of context.
        # Alas, right now, the hover doesn't percolate through, so you don't
        # get mouseover effects. But clicks work.
        objc.classAddMethod( WebHTMLView, "acceptsFirstMouse:", lambda a,b: 1 )
        # ps - when I say 'evil', I mean it. Really, _really_ evil. TODO -
        # subclass the thing and do it properly.

        # create application support folder. The cache goes here. I suppose
        # I should really keep it in a Cache folder somewhere
        folder = os.path.join( os.environ['HOME'], "Library", "Application Support", "Shelf" )
        if not os.path.exists( folder ):
            os.mkdir( folder )



        # Add a handler for the event GURL/GURL. One might think that
        # Carbon.AppleEvents.kEISInternetSuite/kAEISGetURL would work,
        # but the system headers (and hence the Python wrapper for those)
        # are wrong.
        manager = NSAppleEventManager.sharedAppleEventManager()

        manager.setEventHandler_andSelector_forEventClass_andEventID_(
            self, 'handleURLEvent:withReplyEvent:', fourCharToInt( "GURL" ), fourCharToInt( "GURL" ))

    # this is called once we're all launched. Bouncing all over now. 
    def applicationDidFinishLaunching_(self, sender):
        # There's no initial context.
        self.fade()

        # start polling right away
        self.performSelector_withObject_afterDelay_( 'poll', None, 0 )


    # we've been told to close
    def applicationWillTerminate_(self, sender):
        # if we're doing anything in the background, stop it.
        if self.current_clue:
            self.current_clue.stop()

        # kill the poller and any other long-running things
        NSObject.cancelPreviousPerformRequestsWithTarget_( self )


    # This is the callback from the little right-pointing arrow on the main
    # window, to the right of the person icon. Means 'open in address book'
    def openRecord_(self, thing):
        if self.current_clue:
            NSWorkspace.sharedWorkspace().openURL_(
                NSURL.URLWithString_("addressbook://%s"%self.current_clue.uniqueId())
            )

    def hotKeyPressed(self):
        # TODO - this list here is a vage grab-bag of things I want to happen.
        # Should think about how we want to feedback on a deliberate poll,
        # and how to fade the window.
        self.current_clue = None
        self.fade()
        self.deferFade(3) # cause the window to vanish again if we don'e find anything
        self.window().setHidesOnDeactivate_( False )
        self.showWindow_(self)
        self.window().display()
        self.window().orderFrontRegardless()
        self.poll()
    
    # return an Extractor class instance (confusingly called 'handler' for now. Must fix..)
    # for the app with the passed bundle name.
    def handler_for( self, bundle ):
        if not bundle: return None
        
        # haven't seen this application before? Look for a file on disk with
        # the right name and load it.
        if not bundle in self.handlers:
            # convert bundlename to classname like 'ComAppleMail'
            classname = re.sub(r'\.(\w)', lambda m: m.group(1).upper(), bundle )
            classname = re.sub(r'^(\w)', lambda m: m.group(1).upper(), classname )
            
            print_info("** importing file for class %s"%( classname ))
            try:
                # this imports the module with the name 'clasname'.py as the local variable mod
                mod = __import__(classname, globals(), locals(), [''])
                # then get the single class attribute from that module object
                cls = getattr( mod, classname )
                # instantiate the class, and remember it so we don't do this again
                self.handlers[ bundle ] = cls()
            except ImportError:
                import traceback
                print_info( "** Couldn't import file for %s"%( classname ) )
                print_info( traceback.format_exc () )
                self.handlers[ bundle ] = None

        return self.handlers[ bundle ]

    # the main poll loop. Called regularly.
    def poll(self):
        print_info( "\n---- poll start ----" )
        
        # First thing I do, schedule the next poll event, so that I can just return with impunity from this function
        if not NSUserDefaults.standardUserDefaults().boolForKey_("useHotkey"):
            self.performSelector_withObject_afterDelay_( 'poll', None, 4 )

        # get bundle name of active application
        try:
            bundle = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationBundleIdentifier']
        except KeyError:
            # have seen this in the real world. Can't explain it.
            print( "Inexplicable lack of 'NSApplicationBundleIdentifier' for %s"%repr( NSWorkspace.sharedWorkspace().activeApplication() ) )
            return

        print_info( "current app is %s"%bundle )

        # this app has no effect on the current context, otherwise activating
        # the app drops the current context. TODO - don't hard-code bundle name
        if bundle.lower() in ["org.jerakeen.pyshelf"]:
            print_info("Ignoring myself")
            self.deferFade()
            return

        handler = self.handler_for( bundle )
        if not handler:
            print_info("Don't know how to get clues from %s"%bundle)
            return

        self.performSelector_withObject_afterDelay_("lookForCluesWith:", handler, 0)
    
    def lookForCluesWith_( self, handler ):
        # tell the handler to look for clues. Pass it 'self' so that it
        # can call us back
        handler.getClue(self)


    # callback from getClue on the handler function
    def gotClue(self, clue):
        self.deferFade() # put off the context fade

        if self.current_clue and self.current_clue == clue:
            # the context hasn't changed. Don't do anything.
            return

        # clue has changed
        print_info("New context - %s"%clue)
        if self.current_clue:
            self.current_clue.stop()
        self.current_clue = clue
        self.performSelector_withObject_afterDelay_('updateInfo', None, 0 )

    
    # fade the active context if we don't recieve any context for a while.
    # call this method every time something interesting happens, and it'll
    # stop the window going away for another few seconds. That way, I don't
    # have to explicitly watch for 'nothing happened'.
    def deferFade(self, count = 5):
        NSObject.cancelPreviousPerformRequestsWithTarget_selector_object_( self, "fade", None )
        self.performSelector_withObject_afterDelay_('fade', None, count )
    
    # Put window into 'no context, fall to background' state, clear current state
    def fade(self):
        if NSUserDefaults.standardUserDefaults().boolForKey_("useHotkey") and self.current_clue:
            # if we're hotkey driven, don't passively fade ever
            return

        print_info("fading...")
        if self.current_clue:
            self.current_clue.stop()
        self.current_clue = None

        self.window().setLevel_( NSNormalWindowLevel ) # unstuff from 'on top'
        self.window().setHidesOnDeactivate_( True ) # hide window if we have nothing

        self.nameView.setStringValue_( "" )
        self.companyView.setStringValue_( "" )
        self.imageView.setImage_( NSImage.imageNamed_("NSUser") )
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.setWebContent_( "" )

    # put the window into 'I have context' state, display the header, and
    # tell the Clue object to start fetching state about itself.
    def updateInfo(self):
        clue = self.current_clue
        if not clue: return
        clue.setDelegate_(self) # so the clue can send us 'I have updated' messages

        self.nameView.setStringValue_( clue.displayName() )
        self.companyView.setStringValue_( clue.companyName() )
        self.imageView.setImage_( clue.image() ) # does this leak?
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.setWebContent_( clue.content() ) # will initially be 'thinking..'
        
        # always safe
        self.window().setHidesOnDeactivate_( False )
        
        if NSUserDefaults.standardUserDefaults().boolForKey_("bringAppForward"):
            # slightly voodoo, this. But otherwise it doesn't seem 100% reliable
            self.showWindow_(self)
            self.window().orderFrontRegardless()

        if NSUserDefaults.standardUserDefaults().boolForKey_("alwaysOnTop"):
            self.window().setLevel_( NSFloatingWindowLevel ) # 'on top'

        self.window().display()
        
        # do this so we can return to the main runloop ASAP, so the
        # webview has a chance to display something.
        self.performSelector_withObject_afterDelay_('kickClue', None, 0 )


    def kickClue(self):
        if self.current_clue:
            self.current_clue.start()

    # called from the clue when it's updated itself and wants to add to the webview
    def updateWebContent_fromClue_(self, content, clue):
        # old clues may still expect to be able to update the data.
        if clue == self.current_clue:
            self.setWebContent_( content )

    def setWebContent_(self, html):
        # the base path of the webview is the resource folder, so I can use
        # relative paths to refer to the CSS.
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.webView.mainFrame().loadHTMLString_baseURL_( """
            <html>
              <head>
                <link rel="stylesheet" href="%s" type="text/css" />                
              </head>
              <body>
              %s
              <body>
            </html>
        """%(
            #"file:///Users/tomi/svn/Projects/Shelf/style.css?%s"%int(epoch_time()), # dev
            "style.css", # live
            html
        ), base )

    # supress the 'reload' item from the right-click menu - it makes no sense
    def webView_contextMenuItemsForElement_defaultMenuItems_( self, webview, element, items ):
        return filter( lambda i: i.title() != "Reload", items )

    # stolen from djangokit. When the webview wants to fetch a resource,
    # it means either 'I want a file off disk to serve this page' (ok, then)
    # or 'I want to follow this link' (no, I'll just get the system to do that).
    def webView_decidePolicyForNavigationAction_request_frame_decisionListener_( self, webview, action, request, frame, listener):
        url = request.URL()

        # serve files
        if url.scheme() == 'file' or url.scheme() == 'about': # local files
            listener.use()
            return
            
        # everything else can be ignored, and opened by the system
        listener.ignore()
        NSWorkspace.sharedWorkspace().openURL_( url )

    def getDopplrToken_(self, sender):
        url = "https://www.dopplr.com/api/AuthSubRequest?scope=http://www.dopplr.com&next=shelf://shelf/&session=1"
        NSWorkspace.sharedWorkspace().openURL_( NSURL.URLWithString_(url) )

    def handleURLEvent_withReplyEvent_(self, event, replyEvent):
        theURL = event.descriptorForKeyword_(fourCharToInt('----'))
        
        matches = re.search(r'token=(.*)', theURL.stringValue())
        if matches:
            token = matches.group(1)
            url = "https://www.dopplr.com/api/AuthSubSessionToken?token=%s"%( token )
            Cache.getContentOfUrlAndCallback( callback = self.gotDopplrToken, url = url, timeout = 3600, wantStale = False )
            return
        else:
            alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                "Shelf", "Continue", None, None, "Failed to get token - sorry.")

        self.prefsWindow.display()
        self.prefsWindow.makeKeyAndOrderFront_(self)
        alert.beginSheetModalForWindow_modalDelegate_didEndSelector_contextInfo_(
          self.prefsWindow, self, None, None)


    def gotDopplrToken(self, data, stale):
        matches = re.search(r'Token=(.*)', data)
        if matches:
            token = matches.group(1)
            NSUserDefaults.standardUserDefaults().setObject_forKey_(token, "dopplrToken")
            NSUserDefaults.standardUserDefaults().synchronize()
            alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                "Shelf", "Continue", None, None, "Got a Dopplr token!")
        else:
            alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                "Shelf", "Continue", None, None, "Failed to get token - sorry.")

        self.prefsWindow.display()
        self.prefsWindow.makeKeyAndOrderFront_(self)
        alert.beginSheetModalForWindow_modalDelegate_didEndSelector_contextInfo_(
          self.prefsWindow, self, None, None)
    

def fourCharToInt(code):
    return struct.unpack('>l', code)[0]

