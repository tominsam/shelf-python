from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *

import urllib, urllib2
import base64
import os
import re
from time import time
import traceback

from Utilities import *
import Cache

MAX_SORT_ORDER = 999999999999
MIN_SORT_ORDER = 1

class ProviderAtom( object ):
    def __init__(self, provider, url):
        self.provider = provider
        self.url = url
        self.name = url
        self.stale = False
        self.dead = False
        self.error = None
        self.guessed = False
    
    def title(self):
        spinner_html = ""
        if self.guessed:
            spinner_html += ' <img src="guess.png" class="guess"> '
        if self.stale:
            spinner_html += self.provider.spinner()
        return "<h3><a href='%s'>%s%s</a></h3>"%(self.url,self.name,spinner_html)

    def body(self):
        return ""

    def sortOrder(self):
        return MIN_SORT_ORDER

    def content(self):
        if self.dead:
            return ""
        elif self.error:
            return "" # don't display error self.title() + "<pre>%s</pre>"%html_escape(unicode( self.error ))
        else:
            body = self.body()
            if body or self.stale:
                return self.title() + body
            return ""

    def changed(self):
        self.provider.changed()
    
class Provider( object ):
    
    PROVIDERS = []
    
    @classmethod
    def addProvider( myClass, classname ):
        cls = __import__(classname, globals(), locals(), [''])
        Provider.PROVIDERS.append(getattr(cls, classname))
    
    @classmethod
    def providers( myClass ):
        return Provider.PROVIDERS

    def __init__(self, clue):
        #NSLog("** Provider '%s' init"%self.__class__.__name__)
        super( Provider, self ).__init__()
        self.atoms = []
        self.running = True
        self.clue = clue

    def atomClass(self):
        return ProviderAtom
        
    def changed(self):
        self.clue.changed()

    def provide( self ):
        pass
    
    def stop(self):
        # not enforced, it's just a hint to the processor to stop
        NSObject.cancelPreviousPerformRequestsWithTarget_( self )
        self.running = False
    

    def spinner(self):
        return "<img src='spinner.gif' class='spinner'>"
        
