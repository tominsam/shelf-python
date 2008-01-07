from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
import urllib

import re

from threading import Thread

class Provider( Thread ):
    
    PROVIDERS = []

    @classmethod
    def addProvider( myClass, classname ):
        cls = __import__(classname, globals(), locals(), [''])
        Provider.PROVIDERS.append(getattr(cls, classname))
    
    @classmethod
    def providers( myClass ):
        return Provider.PROVIDERS


    def __init__(self, person, delegate):
        #NSLog("** Provider '%s' init"%self.__class__.__name__)
        super( Provider, self ).__init__()
        self.atoms = []
        self.running = True
        self.person = person
        self.delegate = delegate
        self.provide()
    
    def changed(self):
        if self.running:
            self.delegate.providerUpdated_(self)
    
    def stop(self):
        # not enforced, it's just a hint to the processor to stop
        self.running = False
        self.atoms = []
    
    def provide( self ):
        pass
    
    
    CACHE = {}
    def cacheUrl( self, url ):
        if not url in Provider.CACHE:
            Provider.CACHE[url] = None # so that other threads don't try to fetch
            # TODO - put a 'defer' object here if we're fetching it, other
            # threads can wait till we have it. Caching is _hard_
            Provider.CACHE[url] = urllib.urlopen(url).read()
        return Provider.CACHE[url]
