from threading import Thread, Lock
from time import time, sleep

from Utilities import _info

class Cache( object ):

    CACHE = {}
    CACHE_LOCK = Lock()
    
    @classmethod
    def getStale( cls, key ):
        if key in Cache.CACHE and 'value' in Cache.CACHE[key]:
            return Cache.CACHE[key]['value']
        

    @classmethod
    def getFresh( cls, key ):
        if not key in Cache.CACHE:
            return None

        while 'defer' in Cache.CACHE[key] and Cache.CACHE[key]['defer'] and Cache.CACHE[key]['expires'] > time():
            _info( "  other thread is fetching %s"%key )
            sleep(0.5)

        if 'expires' in Cache.CACHE[key] and Cache.CACHE[key]['expires'] > time():
            #_info( "  non-expired cache value for  %s"%key )
            if 'value' in Cache.CACHE[key]:
                return Cache.CACHE[key]['value']

        return None
    
    @classmethod
    def set( cls, key, value, defer = False ):
        cls.lock()
        if not key in Cache.CACHE: Cache.CACHE[key] = {}
        Cache.CACHE[key]['expires'] = time() + 45
        if defer:
            Cache.CACHE[key]['defer'] = True
        else:
            Cache.CACHE[key]['defer'] = False
        if value:
            Cache.CACHE[key]['value'] = value
        cls.unlock()
    
    @classmethod
    def defer( cls, key ):
        cls.set( key, None, True )

    @classmethod
    def lock(cls):
        Cache.CACHE_LOCK.acquire()

    @classmethod
    def unlock(cls):
        Cache.CACHE_LOCK.release()
