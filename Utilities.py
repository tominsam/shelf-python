from Foundation import *
from AppKit import *

def dump( obj ):
    methods = dir(obj)
    for x in dir(object()) + dir(NSObject.alloc().init()):
        if x in methods: methods.remove(x)
    methods.sort()
    print( obj.__class__.__name__ )
    print( "\n".join(map(lambda x: " - %s"%x, methods) ) )

