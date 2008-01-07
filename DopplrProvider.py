from Provider import *
import urllib
import re
import simplejson

class DopplrProvider( Provider ):

    def provide( self ):
        dopplrs = self.person.takeUrls(r'dopplr\.com/traveller')
        if dopplrs:
            self.username = re.search(r'/traveller/([^/]+)', dopplrs[0]).group(1)
            self.atoms = [ "<h3>Fetching Dopplr status</h3>" ]
            self.changed()
            self.start()
    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()        

        #token = "06cb1750a59871aa56e7a4212adbdf19"
        #url = "https://www.dopplr.com/api/"
        #urllib.urlopen(url)
        
        self.atoms = [ "<h3>Dopplr</h3><p>dopplr username is %s</p>"%self.username ]
        
        self.changed()


Provider.PROVIDERS.append( DopplrProvider )
