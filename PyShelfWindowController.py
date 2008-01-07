from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
from ScriptingBridge import *

import objc
import re
import traceback

from Provider import *
import BasicProvider
#import FeedProvider # slow

class ShelfController (NSWindowController):
    companyView = objc.IBOutlet()
    imageView = objc.IBOutlet()
    nameView = objc.IBOutlet()
    webView = objc.IBOutlet()

    def awakeFromNib(self):
        self.handlers = {}
        self.current_person = None
        
    def applicationDidFinishLaunching_(self, sender):
        self.performSelector_withObject_afterDelay_( 'poll', None, 0 )
        self.blank_info()

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
                NSLog( "** Couldn't import file for %s"%( classname ) )
                self.handlers[ bundle ] = None

        return self.handlers[ bundle ]

    def poll(self):
        #NSLog( "..polling.." )
        
        # get bundle name of active application
        bundle = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationBundleIdentifier']
        
        handler = self.handler_for( bundle )
        if handler:
            try:
                clues = handler.clues()
                if len(clues) == 0:
                    NSLog("No clues from %s"%handler.__class__.__name__)
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
            except:
                NSLog("Error getting clues from %s!"%bundle)
                print( traceback.format_exc() )

        self.performSelector_withObject_afterDelay_( 'poll', None, 1 )


    
    def blank_info(self):
        self.nameView.setStringValue_( "" )
        self.companyView.setStringValue_( "" )
        self.imageView.setImageFrameStyle_( NSImageFrameNone )
        self.imageView.setImage_( None )
        self.window().setLevel_( NSFloatingWindowLevel ) # stuff to 'on top'
        self.webView.mainFrame().loadHTMLString_baseURL_( "No context", None )
    
    def update_info_for( self, person ):
        self.nameView.setStringValue_( person.displayName() )
        self.companyView.setStringValue_( person.companyName() )
        self.imageView.setImageFrameStyle_( NSImageFrameNone )
        self.imageView.setImage_( person.image() ) # leak?
        self.window().setLevel_( NSFloatingWindowLevel ) # stuff to 'on top'
        self.webView.mainFrame().loadHTMLString_baseURL_( "thinking..", None )

        try:
            info = []
            for provider in Provider.PROVIDERS:
                info += provider.about( person )
        except:
            NSLog("Failed to get info about person:")
            print(traceback.format_exc())
            info = [ "EPIC FAIL", "<pre>%s</pre>"%traceback.format_exc() ] # TODO - escape html
            
        
        self.webView.mainFrame().loadHTMLString_baseURL_( "".join(info), None )


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

