from Foundation import *
from AppKit import *
from WebKit import *

from threading import Thread, Lock
from time import time, sleep
import base64
import urllib
import os

from Utilities import _info

CACHE = {}
CACHE_LOCK = Lock()

def keyForUrlUsernamePassword( url, username, password ):
    return "%s:::%s:::%s"%( url, username, password )

def filenameForKey( key ):
    folder = os.path.join( os.environ['HOME'], "Library", "Application Support", "Shelf", "cache" )
    try:
        os.makedirs( folder )
    except OSError:
        pass
    filename = urllib.quote( key, '' )
    return os.path.join( folder, filename )

def getStale( key ):
    if key in CACHE and 'value' in CACHE[key]:
        return CACHE[key]['value']
    
def getFresh( key ):
    if not key in CACHE:
        return None

    while 'defer' in CACHE[key] and CACHE[key]['defer'] and CACHE[key]['expires'] > time():
        _info( "  other thread is fetching %s"%key )
        sleep(0.5)

    if 'expires' in CACHE[key] and CACHE[key]['expires'] > time():
        #_info( "  non-expired cache value for  %s"%key )
        if 'value' in CACHE[key]:
            return CACHE[key]['value']

    return None

def set( key, value, defer = False ):
    lock()
    if not key in CACHE: CACHE[key] = {}
    CACHE[key]['expires'] = time() + 45
    if defer:
        CACHE[key]['defer'] = True
    else:
        CACHE[key]['defer'] = False
    if value:
        CACHE[key]['value'] = value
    unlock()

def defer( key ):
    set( key, None, True )

def lock():
    CACHE_LOCK.acquire()

def unlock():
    CACHE_LOCK.release()

def getContentOfUrlAndCallback( callback, url, username = None, password = None ):
    
    filename = filenameForKey( keyForUrlUsernamePassword( url, username, password ) )
    _info("fetching %s to %s"%( url, filename ))

    req = NSMutableURLRequest.requestWithURL_( NSURL.URLWithString_( url ) )
    if username or password:
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
        req.setValue_forHTTPHeaderField_("Basic %s"%base64string, "Authorization")
    
    delegate = DownloadDelegate( callback )
    downloader = NSURLDownload.alloc().initWithRequest_delegate_( req, delegate )
    downloader.setDestination_allowOverwrite_( filename, True )


class DownloadDelegate(object):
    
    def __init__(self, callback):
        self.callback = callback
    
    def downloadDidBegin_(self, downloader):
        print("*** begun download of %s"%downloader.request())
    
    def download_didCreateDestination_(self, downloader, filename):
        print("*** downlaoder created %s"%filename)
        self.filename = filename
    
    def downloadDidFinish_(self, downloader):
        print("*** finished download of %s"%downloader.request())
        data = file( self.filename ).read()
        print(data)
        self.callback( data )

    def download_didFailWithError_(self, downloader, error):
        print("*** ERROR! %s"%error)

