from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
import urllib

import re
from time import time, sleep
import traceback

from threading import Thread, Lock

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
        
    def guardedRun(self):
        pass
        
    def run(self):
        try:
            self.guardedRun()
        except:
            print("EPIC FAIL in %s"%self.__class__.__name__)
            print(traceback.format_exc())
            self.atoms = ["<h3>EPIC FAIL in %s</h3>"%self.__class__.__name__,"<pre>%s</pre>"%traceback.format_exc() ]
            self.changed()


    CACHE = {}
    CACHE_LOCK = Lock()
    def cacheUrl( self, url, timeout = 600 ):
        #print "cacheUrl( %s )"%url
        if url in Provider.CACHE:
            while 'defer' in Provider.CACHE[url] and Provider.CACHE[url]['expires'] > time():
                #print "  other thread is fetching %s"%url
                sleep(0.5)
            if 'expires' in Provider.CACHE[url] and Provider.CACHE[url]['expires'] > time():
                #print "  non-expired cache value for  %s"%url
                return Provider.CACHE[url]['value']
        
        # ok, the cached value has expired. Indicate that this thread
        # will get the value anew. 30 second timeout on this promise.
        Provider.CACHE_LOCK.acquire()
        Provider.CACHE[url] = { 'defer':True, 'expires':time() + 30 }
        Provider.CACHE_LOCK.release()
        data = urllib.urlopen(url).read()
        #print "  got data for %s"%url
        Provider.CACHE_LOCK.acquire()
        Provider.CACHE[url] = { 'expires':time() + timeout, 'value':data }
        Provider.CACHE_LOCK.release()
        return Provider.CACHE[url]['value']
