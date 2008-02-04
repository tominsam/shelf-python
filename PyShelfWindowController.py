from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

import objc
import re
import traceback
import threading
import os
from time import time as epoch_time

from Provider import *
Provider.addProvider( "BasicProvider" )
Provider.addProvider( "TwitterProvider" )
Provider.addProvider( "DopplrProvider" )
Provider.addProvider( "FlickrProvider" )
# Order is important - FeedProvider must be _last_
Provider.addProvider( "FeedProvider" )

from Utilities import _info

class ShelfController (NSWindowController):
    companyView = objc.IBOutlet()
    imageView = objc.IBOutlet()
    nameView = objc.IBOutlet()
    webView = objc.IBOutlet()

    def awakeFromNib(self):
        self.handlers = {}
        self.providers = []
        self.current_person = None
        self.running = True

        #self.window().setAllowsToolTipsWhenApplicationIsInactive_( 1 )
        #self.window().setAlphaValue_( 0.9 )
        
        bg = self.window().backgroundColor().colorUsingColorSpaceName_( NSCalibratedRGBColorSpace )
        rgb = "%x%x%x"%(
            bg.redComponent() * 255.999999,
            bg.greenComponent() * 255.999999,
            bg.blueComponent() * 255.999999
        )
        # TODO - ok. Now do something with this information. Specifically,
        # get it into the CSS.
        
        # evil. Alter the webkit view object so that it'll accept a clickthrough
        # - this is very handy, as the window is on top and full of context.
        # Alas, right now, the hover doesn't percolate through, so you don't
        # get mouseover effects. But clicks work.
        objc.classAddMethod( WebHTMLView, "acceptsFirstMouse:", lambda a,b: 1 )
        # ps - when I say 'evil', I mean it. Really, _really_ evil. TODO -
        # subclass the thing and do it properly.

        
    def applicationDidFinishLaunching_(self, sender):
        folder = os.path.join( os.environ['HOME'], "Library", "Application Support", "Shelf" )
        if not os.path.exists( folder ):
            os.mkdir( folder )
        Provider.load_cache( os.path.join( folder, "cache" ) )
        self.performSelector_withObject_afterDelay_( 'poll', None, 0 )
        self.fade()
    
    def applicationWillTerminate_(self, sender):
        for current in self.providers:
            current.stop()

        folder = os.path.join( os.environ['HOME'], "Library", "Application Support", "Shelf" )
        Provider.load_cache( os.path.join( folder, "cache" ) )
        Provider.store_cache( "/tmp/shelf_cache" )

        self.running = False
        
    # callback from the little right-pointing arrow
    def openRecord_(self, thing):
        if self.current_person:
            NSWorkspace.sharedWorkspace().openURL_(
                NSURL.URLWithString_("addressbook://%s"%self.current_person.uniqueId())
            )

    def handler_for( self, bundle ):
        if not bundle: return None
        if not bundle in self.handlers:
            # convert bundlename to classname like 'ComAppleMail'
            classname = re.sub(r'\.(\w)', lambda m: m.group(1).upper(), bundle )
            classname = re.sub(r'^(\w)', lambda m: m.group(1).upper(), classname )
            
            try:
                mod = __import__(classname, globals(), locals(), [''])
                cls = getattr( mod, classname )
                self.handlers[ bundle ] = cls()
            except ImportError:
                _info( "** Couldn't import file for %s"%( classname ) )
                self.handlers[ bundle ] = None

        return self.handlers[ bundle ]

    def poll(self):
        _info( "\n---- poll start ----" )
        
        # First thing I do, schedule the next poll event, so that I can just return with impunity later
        if self.running:
            self.performSelector_withObject_afterDelay_( 'poll', None, 2 )


        # get bundle name of active application
        try:
            bundle = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationBundleIdentifier']
        except KeyError:
            # have seen this in the real world. Can't explain it.
            print( "Inexplicable lack of 'NSApplicationBundleIdentifier' for %s"%repr( NSWorkspace.sharedWorkspace().activeApplication() ) )
            return

        _info( "current app is %s"%bundle )

        # this app has no effect on the current context, otherwise activating
        # the app drops the current context.
        if bundle.lower() in ["org.jerakeen.pyshelf"]:
            _info("Ignoring myself")
            return

        handler = self.handler_for( bundle )
        
        if not handler:
            _info("Don't know how to get clues from %s"%bundle)
            return
        else:
            _info( "Looking for clues using %s"%handler )
            handler.getClue( self )
            self.deferFade() # if nothing happens for 5 seconds, hide context

    # fade the active context if we don't recieve any context for a while
    def deferFade(self):
        _info("deferring fade")
        NSObject.cancelPreviousPerformRequestsWithTarget_selector_object_( self, "fade", None )
        self.performSelector_withObject_afterDelay_('fade', None, 5 )
    
    # callback from getClue on the handler function
    def gotClue(self, person):
        
        if self.current_person and self.current_person == person:
            _info("Context has not changed")
            self.deferFade() # put off the context fade
            return

        # person has changed
        _info("New context - %s"%person)
        self.current_person = person
        self.update_info_for( person )
        _info("update complete")

    
    def fade(self):
        _info("fading context")
        self.current_person = None
        self.nameView.setStringValue_( "" )
        self.companyView.setStringValue_( "" )
        self.imageView.setImage_( NSImage.imageNamed_("NSUser") )
        self.window().setLevel_( NSNormalWindowLevel ) # stuff to 'on top'
        self.window().setHidesOnDeactivate_( True )
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.setWebContent( "<p>No context</p>" )


    def update_info_for( self, person ):
        _info("updating header")
        self.nameView.setStringValue_( person.displayName() )
        self.companyView.setStringValue_( person.companyName() )
        self.imageView.setImage_( person.image() ) # leak?
        self.window().setLevel_( NSFloatingWindowLevel ) # stuff to 'on top'
        self.window().setHidesOnDeactivate_( False )
        self.showWindow_(self)
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.setWebContent( "<p>thinking..</p>" )

        _info( "stopping %s old providers"%len( self.providers ) )
        for current in self.providers:
            current.stop()

        _info( "creating new providers" )
        self.providers = []
        for cls in Provider.providers():
            try:
                self.providers.append( cls( person, self ) )
            except:
                print("Failed to create provider %s for person:"%cls)
                print(traceback.format_exc())
        _info( "update done" )

    def updateWebview(self):
        _info( "updating webview" )
        info = []
        for provider in self.providers:
            info += provider.atoms
        self.setWebContent( "".join(info) )
    
    def setWebContent(self, html):
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
        _info( "webview update complete" )

    def providerUpdated_(self, provider):
        _info("Provider '%s' updated"%( provider ))
        self.performSelectorOnMainThread_withObject_waitUntilDone_('updateWebview', None, False)

    # supress right-click menu
    def webView_contextMenuItemsForElement_defaultMenuItems_( self, webview, element, items ):
        return filter( lambda i: i.title() != "Reload", items )

    # stolen from djangokit
    def webView_decidePolicyForNavigationAction_request_frame_decisionListener_( self, webview, action, request, frame, listener):
        url = request.URL()

        # serve files
        if url.scheme() == 'file' or url.scheme() == 'about':
            listener.use()
            return
            
        # everything else can be ignored, and opened by the system
        listener.ignore()
        NSWorkspace.sharedWorkspace().openURL_( url )

