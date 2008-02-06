from Foundation import *
from AppKit import *
from WebKit import *

from time import time, sleep
import base64
import urllib
import os
import os.path
import hashlib

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
def getContentOfUrlAndCallback( callback, url, username = None, password = None, wantStale = False, timeout = 600, failure = None ):
    
    filename = filenameForKey( keyForUrlUsernamePassword( url, username, password ) )

    if os.path.exists(filename):
        if time() - os.path.getmtime( filename ) < timeout:
            callback( file( filename ).read(), False )
            return # no need to get the URL
        
        elif wantStale:
            # call the callback immediately with the stale data.
            print_info("We have stale data")
            callback( file( filename ).read(), True )
            # don't return - we still want to fetch the file
    
    # TODO - if we're already fetching the file on behalf of someone
    # else, it would be nice to do the Right Thing here.

    req = NSMutableURLRequest.requestWithURL_( NSURL.URLWithString_( url ) )
    if username or password:
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
        req.setValue_forHTTPHeaderField_("Basic %s"%base64string, "Authorization")

    # Send the right User-Agent. TODO - get the bundle version properly, don't hard-code
    req.setValue_forHTTPHeaderField_("Shelf/0.0.12 +http://jerakeen.org/code/shelf/", "User-Agent")
    
    delegate = DownloadDelegate( callback, failure )
    downloader = NSURLDownload.alloc().initWithRequest_delegate_( req, delegate )
    downloader.setDestination_allowOverwrite_( filename, True )


class DownloadDelegate(object):
    
    def __init__(self, callback, failure):
        self.callback = callback
        self.failure = failure
    
    def downloadDidBegin_(self, downloader):
        print_info("Begun download of %s"%downloader.request())
    
    def download_didCreateDestination_(self, downloader, filename):
        self.filename = filename
    
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
#from objc import Category, YES
#class NSURLRequest(Category(NSURLRequest)):
#    @classmethod
#    def allowsAnyHTTPSCertificateForHost_(cls, host):
#        return YES

