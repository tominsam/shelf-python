from Provider import *
from urllib import quote
import re

class DopplrProvider( Provider ):

    def provide( self ):
        dopplrs = [ u for u in self.person.urls() if re.search(r'www.dopplr.com', u) ]
        if dopplrs:
            self.atoms = [ "<h3>Fetching Dopplr status</h3>" ]
            self.changed()
            self.start()
    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        

        dopplr = [ u for u in self.person.urls if re.search(r'www.dopplr.com', u) ][0]
        
        self.atoms = []
        
        self.changed()


Provider.PROVIDERS.append( DopplrProvider )
