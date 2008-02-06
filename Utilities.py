from Foundation import *
from AppKit import *
from ScriptingBridge import *
from AddressBook import *

import re

def as_dump( obj ):
    methods = dir(obj)
    for x in dir(object()) + dir(NSObject.alloc().init()):
        if x in methods: methods.remove(x)
    methods.sort()
    print( obj.__class__.__name__ )
    print( "\n".join(map(lambda x: " - %s"%x, methods) ) )

def as_app(bundle):
    return SBApplication.applicationWithBundleIdentifier_(bundle)

def print_info(stuff):
    if NSUserDefaults.standardUserDefaults().boolForKey_("debug"):
        print(stuff)

def html_escape( s ):
    s = re.sub(r"&", "&amp;", s)
    s = re.sub(r"<", "&lt;", s)
    s = re.sub(r">", "&gt;", s)
    return s

# this is a HACK to normalize urls. not that it's not required to return
# something that's still a valid url! (though it currently does) Don't assume
# that it does
def normalize_url( url ):
    url = re.sub(r'/$', '', url) # trailing slash
    url = re.sub(r'^\w+://', '', url) # protocol
    url = re.sub(r'^www.flickr.', 'flickr.', url) # flickr special casing
    return url
