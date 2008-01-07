from Provider import *
import urllib
import re
import xmltramp

class DopplrProvider( Provider ):
    cache = {}

    def provide( self ):
        self.token = NSUserDefaults.standardUserDefaults().stringForKey_("dopplrToken")
        dopplrs = self.person.takeUrls(r'dopplr\.com/traveller')
        if not dopplrs or not self.token: return
    
        self.username = re.search(r'/traveller/([^/]+)', dopplrs[0]).group(1)
        self.atoms = [ "<h3>Dopplr&nbsp;<img src='spinner.gif'></h3>" ]
        self.changed()

        self.start()
    
    def run(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()
        
        if not self.username in DopplrProvider.cache:
            DopplrProvider.cache[ self.username ] = None
            url = "https://www.dopplr.com/api/traveller_info.xml?token=%s&traveller=%s"%( self.token, self.username )
            DopplrProvider.cache[ self.username ] = xmltramp.load( url )
        
        doc = DopplrProvider.cache[ self.username ]
        
        if doc:
            self.atoms = [ "<h3>Dopplr</h3><p>%s %s</p>"%( self.person.displayName(), doc.traveller.status ) ]
        else:
            self.atoms = []
        
        self.changed()
