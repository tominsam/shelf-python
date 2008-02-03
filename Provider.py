from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *
import urllib, urllib2
import base64

# force shelve to use the native python pickler
import shelve
import pickle
shelve.Pickler = pickle.Pickler
shelve.Unpickler = pickle.Unpickler

import os

from Utilities import _info

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
    
    def provide( self ):
        self.start()
        
    def guardedRun(self):
        pass
        
    def run(self):
        pool = NSAutoreleasePool.alloc().init()
        try:
            self.guardedRun()
        except Exception, e:
            print("EPIC FAIL in %s"%self.__class__.__name__)
            print(traceback.format_exc())
            self.atoms = ["<h3>EPIC FAIL in %s</h3>"%self.__class__.__name__,"<pre>%s</pre>"%e ]
            self.changed()


    CACHE = None
    CACHE_LOCK = Lock()

    @classmethod
    def store_cache( myClass, filename ):
        pass
        #Provider.CACHE_LOCK.acquire()
        #Provider.CACHE.close()
        #Provider.CACHE_LOCK.release()

    @classmethod
    def load_cache( myClass, filename ):
        Provider.CACHE_LOCK.acquire()
        #try:
        #    Provider.CACHE = shelve.open( filename, writeback = True )
        #except Exception:
        #    print("cache file bad - invalidating")
        #    os.unlink( filename + ".db" )
        #    Provider.CACHE = shelve.open( filename, writeback = True )
        Provider.CACHE = {}
        Provider.CACHE_LOCK.release()

    def keyForUrlUsernamePassword( self, url, username, password ):
        return url + (username or "") + (password or "")

    def staleUrl( self, url, username = None, password = None ):
        key = self.keyForUrlUsernamePassword(url, username, password)
        print(key)
        if key in Provider.CACHE and 'value' in Provider.CACHE[key]:
            return Provider.CACHE[key]['value']
        
    def cacheUrl( self, url, timeout = 600, username = None, password = None ):
        key = self.keyForUrlUsernamePassword(url, username, password)
        _info( "cacheUrl( %s )"%url )
        if key in Provider.CACHE:
            while 'defer' in Provider.CACHE[key] and Provider.CACHE[key]['defer'] and Provider.CACHE[key]['expires'] > time():
                #_info( "  other thread is fetching %s"%url )
                sleep(0.5)
            if 'expires' in Provider.CACHE[key] and Provider.CACHE[key]['expires'] > time():
                #_info( "  non-expired cache value for  %s"%url )
                if 'value' in Provider.CACHE[key]:
                    return Provider.CACHE[key]['value']

        # ok, the cached value has expired. Indicate that this thread
        # will get the value anew. There's a timeout on this promise.
        Provider.CACHE_LOCK.acquire()
        if not key in Provider.CACHE: Provider.CACHE[key] = {}
        Provider.CACHE[key]['defer'] = True
        Provider.CACHE[key]['expires'] = time() + 45
        Provider.CACHE_LOCK.release()

        # use urllib2 here because urllib prompts on stdout if
        # the feed needs auth. Stupid.
        req = urllib2.Request(url)
        if username or password:
            base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
            req.add_header("Authorization", "Basic %s" % base64string)        
        needs_auth = False
        try:
            data = urllib2.urlopen(req).read()
        except IOError, e:
            print e.__class__.__name__
            if e.code == 401:
                # needs auth. Meh.
                _info("url needs auth - ignoring")
                needs_auth = True
            else:
                print("Error getting url: %s"%e)
            data = None

        Provider.CACHE_LOCK.acquire()
        Provider.CACHE[key]['value'] = data
        Provider.CACHE[key]['defer'] = False
        if data or needs_auth:
            Provider.CACHE[key]['expires'] = time() + timeout
        else:
            Provider.CACHE[key]['expires'] = time() + 10
        Provider.CACHE_LOCK.release()

        return Provider.CACHE[key]['value']

    def spinner(self):
        return "<img src='spinner.gif' class='spinner'>"
        
