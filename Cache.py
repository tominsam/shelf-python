from Foundation import *
from AppKit import *
from WebKit import *

from time import time, sleep
import base64
import urllib
import os
import os.path
import hashlib
import re

from Utilities import *

def keyForUrlUsernamePassword( url, username, password ):
    return "%s:::%s:::%s"%( url, username, password )

def filenameForKey( key ):
    folder = os.path.join( os.environ['HOME'], "Library", "Application Support", "Shelf", "cache" )
    try:
        os.makedirs( folder )
    except OSError:
        pass
    filename = urllib.quote( key, '' )
    # this can make filenames that are waaaay too long
    hasher = hashlib.md5()
    hasher.update(filename)
    return os.path.join( folder, hasher.hexdigest() )

#LAST_CACHE_CLEAN = 0
def cleanCache():
    #if time() - LAST_CACHE_CLEAN < 60:
    #    return

    folder = os.path.join( os.environ['HOME'], "Library", "Application Support", "Shelf", "cache" )
    try:
        files = os.listdir(folder)
    except OSError:
        return

    for file in os.listdir( folder ):
        filename = os.path.join( folder, file )
        # file not looked at in a day
        if time() - os.path.getatime( filename ) > 24 * 3600:
            print_info("Removing old cache file %s"%filename)
            os.unlink( filename )
    
    #LAST_CACHE_CLEAN = time()


# ask Cocoa to download an url and get back to us. It pulls the file to disk locally, and uses this as a cache,
# using mtime. The callback should be a function that will be called
# at some time in the future (BUG - if there's a good cache, it'll be
# called _before_ this function returns. Bad), with 2 params - the data,
# and a true/false if the data is stale or not.
#
# Calling with wantstale of true will call the callback function right away
# if here is _any_ data, even if it's old (BUG - as before, this is called
# before this function returns), then will fetch the data and call the callback
# _again_.
def getContentOfUrlAndCallback(callback, url, username = None, password = None, wantStale = False, timeout = 600, failure = None ):
    cleanCache()
    # I have address book entries that are just 'www.foo.com'
    if not re.match(r'^\w+://', url):
        url = "http://%s"%url

    delegate = DownloadDelegate.alloc().init()
    delegate.callback = callback
    delegate.failure = failure
    delegate.url = url
    delegate.username = username
    delegate.password = password
    delegate.timeout = timeout
    delegate.wantStale = wantStale
    
    delegate.performSelector_withObject_afterDelay_('start', None, 0 )

class DownloadDelegate( NSObject ):
    
    def init(self):
        self = NSObject.init( self )
        if not self: return

        self.callback = None
        self.failure = None
        self.url = None
        self.username = None
        self.password = None
        self.timeout = None
        self.wantStale = None

        return self

    # this is a seperate function so I can call it after a delay
    def start(self):
        filename = filenameForKey( keyForUrlUsernamePassword( self.url, self.username, self.password ) )

        if os.path.exists(filename):
            if time() - os.path.getmtime( filename ) < self.timeout:
                self.callback( file( filename ).read(), False )
                return # no need to get the URL

            elif self.wantStale:
                # call the callback immediately with the stale data.
                print_info("We have stale data")
                self.callback( file( filename ).read(), True )
                # don't return - we still want to fetch the file

        # TODO - if we're already fetching the file on behalf of someone
        # else, it would be nice to do the Right Thing here.

        req = NSMutableURLRequest.requestWithURL_( NSURL.URLWithString_( self.url ) )
        if self.username or self.password:
            base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
            req.setValue_forHTTPHeaderField_("Basic %s"%base64string, "Authorization")

        # Send the right User-Agent. TODO - get the bundle version properly, don't hard-code
        req.setValue_forHTTPHeaderField_("Shelf/0.0.11.9 +http://jerakeen.org/code/shelf/", "User-Agent")
    
        downloader = NSURLDownload.alloc().initWithRequest_delegate_( req, self )
        downloader.setDestination_allowOverwrite_( filename, True )
    
    def downloadDidBegin_(self, downloader):
        print_info("Begun download of %s"%downloader.request())
    
    def download_didCreateDestination_(self, downloader, filename):
        self.filename = filename
        os.utime( self.filename, None )
    
    def downloadDidFinish_(self, downloader):
        # the downloader sets the mtime to be the web server's idea of
        # when the file was last updated. Which is cute. But useless to us.
        # I want to know when I fetched it.
        os.utime( self.filename, None )
        data = file( self.filename ).read()
        self.callback( data, False )

    def download_didFailWithError_(self, downloader, error):
        print("error downloading %s: %s"%( downloader.request(), error ))
        if self.failure:
            self.failure( error )

# incredibly evil - ignore https cert errors (doesn't work!)
#from objc import Category
#class NSURLRequest(Category(NSURLRequest)):
#    @classmethod
#    def allowsAnyHTTPSCertificateForHost_(cls, host):
#        return True


    