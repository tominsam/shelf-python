from Foundation import *
from AppKit import *

def dump( obj ):
    methods = dir(obj)
    [ methods.remove(x) for x in dir(NSObject.alloc().init()) ]
    [ methods.remove(x) for x in dir(object()) ]
    methods.sort()
    print( obj.__class__.__name__ )
    print( "\n".join(map(lambda x: " - %s"%x, methods) ) )

