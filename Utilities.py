from Foundation import *
from AppKit import *
from ScriptingBridge import *
from AddressBook import *

import re

def dump( obj ):
    methods = dir(obj)
    for x in dir(object()) + dir(NSObject.alloc().init()):
        if x in methods: methods.remove(x)
    methods.sort()
    print( obj.__class__.__name__ )
    print( "\n".join(map(lambda x: " - %s"%x, methods) ) )

def app(bundle):
    return SBApplication.applicationWithBundleIdentifier_(bundle)

def _info(stuff):
    if NSUserDefaults.standardUserDefaults().boolForKey_("debug"):
        print(stuff)

def html_escape( s ):
    s = re.sub(r"&", "&amp;", s)
    s = re.sub(r"<", "&lt;", s)
    s = re.sub(r">", "&gt;", s)
    return s
    