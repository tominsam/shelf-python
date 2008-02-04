from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *

import urllib, urllib2
import base64
import os
import re
from time import time, sleep
import traceback

from Utilities import _info
from Cache import Cache


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
        NSObject.cancelPreviousPerformRequestsWithTarget_( self )
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

    def keyForUrlUsernamePassword( self, url, username, password ):
        return url + (username or "") + (password or "")

    def staleUrl( self, url, username = None, password = None ):
        key = self.keyForUrlUsernamePassword(url, username, password)
        return Cache.getStale( key )
        
    def cacheUrl( self, url, timeout = 600, username = None, password = None ):
        key = self.keyForUrlUsernamePassword(url, username, password)
        _info( "cacheUrl( %s )"%url )
        cached = Cache.getFresh( key )

        # ok, the cached value has expired. Indicate that this thread
        # will get the value anew. There's a timeout on this promise.
        Cache.defer( key )

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
        
        Cache.set( key, data )

        return data

    def spinner(self):
        return "<img src='spinner.gif' class='spinner'>"
        
