from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *

import re

class Provider(object):
    
    PROVIDERS = []

    def __init__(self):
        NSLog("** Provider '%s' init"%self.__class__.__name__)
        super( Provider, self ).__init__()

    def about( self, person ):
        return []