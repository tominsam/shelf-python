from Provider import *
import urllib
import re
import xmltramp

class DopplrProvider( Provider ):

    def provide( self ):
        self.token = NSUserDefaults.standardUserDefaults().stringForKey_("dopplrToken")
        dopplrs = self.person.takeUrls(r'dopplr\.com/traveller')
        if not dopplrs or not self.token: return
    
        self.username = re.search(r'/traveller/([^/]+)', dopplrs[0]).group(1)
        self.atoms = [ "<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a>&nbsp;<img src='spinner.gif'></h3>"%( self.username ) ]
        self.changed()

        self.start()
    
    def guardedRun(self):
        print("Running thread")
        pool = NSAutoreleasePool.alloc().init()
        
        url = "https://www.dopplr.com/api/traveller_info.xml?token=%s&traveller=%s"%( self.token, self.username )
        xml = self.cacheUrl( url, timeout = 3600 * 2 )
        doc = xmltramp.parse( xml )
        
        if doc:
            self.atoms = [ "<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a></h3><p>%s %s</p>"%( self.username, self.person.displayName(), doc.traveller.status ) ]
        else:
            self.atoms = []
        
        self.changed()
