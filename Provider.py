from Foundation import *
from AppKit import *
from WebKit import *
from AddressBook import *

import re

from threading import Thread

class Provider( Thread ):
    
    PROVIDERS = []

    def __init__(self, person, delegate):
        NSLog("** Provider '%s' init"%self.__class__.__name__)
        super( Provider, self ).__init__()
        self.atoms = []
        self.running = True
        self.person = person
        self.delegate = delegate
        self.provide()
    
    def changed(self):
        self.delegate.providerUpdated_(self)
    
    def stop(self):
        # not enforced, it's just a hint to the processor to stop
        self.running = False
    
    def provide( self ):
        pass
