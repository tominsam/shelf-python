from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

import objc
import re
import traceback
import threading

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
        
    def applicationDidFinishLaunching_(self, sender):
        self.performSelector_withObject_afterDelay_( 'poll', None, 0 )
        self.blank_info()
    
    def applicationWillTerminate_(self, sender):
        for current in self.providers:
            current.stop()
        
        
    def openRecord_(self, thing):
        if self.current_person:
            NSWorkspace.sharedWorkspace().openURL_(
                NSURL.URLWithString_("addressbook://%s"%self.current_person.uniqueId())
            )

    def handler_for( self, bundle ):
        if not bundle in self.handlers:
            # convert bundlename to classname like 'ComAppleMail'
            classname = re.sub(r'\.(\w)', lambda m: m.group(1).upper(), bundle )
            classname = re.sub(r'^(\w)', lambda m: m.group(1).upper(), classname )
            
            try:
                mod = __import__(classname, globals(), locals(), [''])
                cls = getattr( mod, classname )
                self.handlers[ bundle ] = cls()
            except ImportError:
                #NSLog( "** Couldn't import file for %s"%( classname ) )
                self.handlers[ bundle ] = None

        return self.handlers[ bundle ]

    def poll(self):
        # get bundle name of active application
        bundle = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationBundleIdentifier']
        handler = self.handler_for( bundle )
        
        # this app has no effect on the current context, otherwise activating
        # the app drops the current context. Also, XCode is special so I don't
        # go crazy while debugging. This one should probably come out in the
        # long term.
        if bundle.lower() in ["org.jerakeen.pyshelf", "com.apple.xcode"]:
            pass
        
        elif not handler:
            #NSLog("Can't get clues from %s"%bundle)
            self.current_person = None
            self.blank_info()
        else:
            clues = []
            try:
                clues = handler.clues()
            except:
                NSLog("Error getting clues from %s!"%bundle)
                print( traceback.format_exc() )

            if not clues:
                #NSLog("No clues from %s"%handler.__class__.__name__)
                self.current_person = None
                self.blank_info()
            elif self.current_person and self.current_person.uniqueId() == clues[0].uniqueId():
                pass
                #NSLog("Context has not changed")
            else:
                NSLog("New context - %s"%clues[0].displayName())
                # person has changed
                self.current_person = clues[0]
                self.update_info_for( clues[0] )

        self.performSelector_withObject_afterDelay_( 'poll', None, 1 )


    
    def blank_info(self):
        self.nameView.setStringValue_( "" )
        self.companyView.setStringValue_( "" )
        self.imageView.setImage_( NSImage.imageNamed_("NSUser") )
        self.window().setLevel_( NSNormalWindowLevel ) # stuff to 'on top'
        self.window().setHidesOnDeactivate_( True )
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.webView.mainFrame().loadHTMLString_baseURL_( "No context", base )


    def update_info_for( self, person ):
        self.nameView.setStringValue_( person.displayName() )
        self.companyView.setStringValue_( person.companyName() )
        self.imageView.setImage_( person.image() ) # leak?
        self.window().setLevel_( NSFloatingWindowLevel ) # stuff to 'on top'
        self.window().setHidesOnDeactivate_( False )
        self.showWindow_(self)
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.webView.mainFrame().loadHTMLString_baseURL_( "thinking..", base )

        for current in self.providers:
            current.stop()

        self.providers = []
        for cls in Provider.providers():
            try:
                self.providers.append( cls( person, self ) )
            except:
                NSLog("Failed to create provider %s for person:"%cls)
                print(traceback.format_exc())
                    
    def updateWebview(self):
        info = []
        for provider in self.providers:
            info += provider.atoms
        
        base = NSURL.fileURLWithPath_( NSBundle.mainBundle().resourcePath() )
        self.webView.mainFrame().loadHTMLString_baseURL_( "".join(info), base )

    def providerUpdated_(self, provider):
        #print("Provider '%s' updated"%( provider ))
        self.performSelectorOnMainThread_withObject_waitUntilDone_('updateWebview', None, False)

    # supress right-click menu
    def webView_contextMenuItemsForElement_defaultMenuItems_( self, webview, element, items ):
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

