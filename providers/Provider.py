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

class ProviderAtom( object ):
    def __init__(self, provider, url):
        self.provider = provider
        self.url = url
        self.name = url
        self.stale = True
        self.dead = False
        self.error = None
    
    def title(self):
        if self.stale:
            spinner_html = "&nbsp;" + self.provider.spinner()
        else:
            spinner_html = ""
        return "<h3><a href='%s'>%s%s</a></h3>"%(self.url,self.name,spinner_html)
    
    def body(self):
        return ""

    def sortOrder(self):
        return None

    def content(self):
        if self.dead:
            return ""
        elif self.error:
            return "" # don't display error self.title() + "<pre>%s</pre>"%html_escape(unicode( self.error ))
        else:
            body = self.body()
            if body or self.stale:
                return self.title() + self.body()
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
    
    def content(self):
        def sorter(a, b):
            return cmp( b.sortOrder(), a.sortOrder() )
        self.atoms.sort(sorter)
        return "".join([ atom.content() for atom in self.atoms ])
    
    def changed(self):
        self.clue.providerUpdated_(self)

    def provide( self ):
        pass
    
    def stop(self):
        # not enforced, it's just a hint to the processor to stop
        NSObject.cancelPreviousPerformRequestsWithTarget_( self )
        self.running = False
    

    def spinner(self):
        return "<img src='spinner.gif' class='spinner'>"
        
