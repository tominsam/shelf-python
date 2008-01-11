from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

import objc
import re
import traceback
import threading
from time import time as epoch_time

from Provider import *
Provider.addProvider( "BasicProvider" )
Provider.addProvider( "TwitterProvider" )
Provider.addProvider( "DopplrProvider" )
Provider.addProvider( "FlickrProvider" )
# Order is important - FeedProvider must be _last_
Provider.addProvider( "FeedProvider" )

class ShelfController (NSWindowController):
    companyView = objc.IBOutlet()
    imageView = objc.IBOutlet()
    nameView = objc.IBOutlet()
    webView = objc.IBOutlet()

    def awakeFromNib(self):
        self.handlers = {}
        self.providers = []
        self.current_person = None
        self.decay = 0
        self.window().setAllowsToolTipsWhenApplicationIsInactive_( 1 )
        #self.window().setAlphaValue_( 0.9 )
        
        # evil. Alter the webkit view object so that it'll accept a clickthrough
        # - this si very handy, as the window is on top and full of context.
        # Alas, right now, the hover doesn't percolate through, so you don't
        # get mouseover effects. But clicks work.
        objc.classAddMethod( WebHTMLView, "acceptsFirstMouse:", lambda a,b: 1 )
        
    def applicationDidFinishLaunching_(self, sender):
        self.performSelector_withObject_afterDelay_( 'poll', None, 0 )
        self.blank_info()
    
    def applicationWillTerminate_(self, sender):
        for current in self.providers:
            current.stop()
        
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
                #print( "** Couldn't import file for %s"%( classname ) )
                self.handlers[ bundle ] = None

        return self.handlers[ bundle ]

    def poll(self):
        print "poll start"
        
        # get bundle name of active application
        try:
            bundle = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationBundleIdentifier']
        except KeyError:
            print "Inexplicable lack of 'NSApplicationBundleIdentifier' for %s"%repr( NSWorkspace.sharedWorkspace().activeApplication() )
            bundle = ""
        
        print "app is %s"%bundle

        handler = self.handler_for( bundle )
        
        # this app has no effect on the current context, otherwise activating
        # the app drops the current context. Also, XCode is special so I don't
        # go crazy while debugging. This one should probably come out in the
        # long term.
        if bundle.lower() in ["org.jerakeen.pyshelf", "com.apple.xcode"]:
            print("Ignoring myself")
            pass
        
        elif not handler:
            print("Can't get clues from %s"%bundle)
            self.current_person = None
        else:
            print "Looking for clues"
            clues = []
            try:
                clues = handler.clues()
            except:
                print("Error getting clues from %s!"%bundle)
                print( traceback.format_exc() )

            if not clues:
                print("No clues from %s"%handler.__class__.__name__)
                self.current_person = None

            elif self.current_person and self.current_person.uniqueId() == clues[0].uniqueId():
                print("Context has not changed")
                pass

            else:
                # person has changed
                print("New context - %s"%clues[0].displayName())
                self.current_person = clues[0]
                self.decay = 3
                self.update_info_for( clues[0] )
                print("update complete")

        # rather than removing the window as soon as we lose context, have
        # the display persist a little. Use case here is clicking on a link
        # in the webview - without this we lose context for a tick while the
        # browser thinks about it.
        if not self.current_person and self.decay > 0:
            print("decaying context")
            self.decay -= 1
            if self.decay == 0:
                self.blank_info()

        self.performSelector_withObject_afterDelay_( 'poll', None, 1 )
        print "poll complete"


    
    def blank_info(self):
        self.nameView.setStringValue_( "" )
        self.companyView.setStringValue_( "" )
        self.imageView.setImage_( NSImage.imageNamed_("NSUser") )
        self.window().setLevel_( NSNormalWindowLevel ) # stuff to 'on top'
        self.window().setHidesOnDeactivate_( True )
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.setWebContent( "<p>No context</p>" )


    def update_info_for( self, person ):
        print("updating header")
        self.nameView.setStringValue_( person.displayName() )
        self.companyView.setStringValue_( person.companyName() )
        self.imageView.setImage_( person.image() ) # leak?
        self.window().setLevel_( NSFloatingWindowLevel ) # stuff to 'on top'
        self.window().setHidesOnDeactivate_( False )
        self.showWindow_(self)
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.setWebContent( "<p>thinking..</p>" )

        print "stopping %s old providers"%len( self.providers )
        for current in self.providers:
            current.stop()

        print "creating new providers"
        self.providers = []
        for cls in Provider.providers():
            try:
                self.providers.append( cls( person, self ) )
            except:
                print("Failed to create provider %s for person:"%cls)
                print(traceback.format_exc())
        print "update done"

    def updateWebview(self):
        print "updating webview"
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
        print "webview update complete"

    def providerUpdated_(self, provider):
        print("Provider '%s' updated"%( provider ))
        self.performSelectorOnMainThread_withObject_waitUntilDone_('updateWebview', None, False)

    # supress right-click menu
    def webView_contextMenuItemsForElement_defaultMenuItems_( self, webview, element, items ):
        print repr(items)
        return filter( lambda i: i.title != "Reload", items )

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

