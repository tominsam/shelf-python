from Provider import *
import urllib
import re
import xmltramp
from datetime import datetime

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
        pool = NSAutoreleasePool.alloc().init()
        
        url = "https://www.dopplr.com/api/traveller_info.xml?token=%s&traveller=%s"%( self.token, self.username )
        xml = self.cacheUrl( url, timeout = 3600 * 2 )
        doc = xmltramp.parse( xml )
        
        if not doc:
            self.atoms = []
            self.changed()
            return
        
        # strip timezone and parse. Ewwww
        localtime = datetime.strptime( str(doc.traveller.current_city.localtime)[:19], "%Y-%m-%dT%H:%M:%S")
        offset = str(doc.traveller.current_city.localtime)[19:]

        status = "%s %s. Time in %s is %s (%s)."%(
            self.person.displayName(),
            doc.traveller.status,
            doc.traveller.current_city.country,
            localtime.strftime("%a %I:%M %p"),
            offset
        )
        self.atoms = [ "<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a></h3><p>%s</p>"%( self.username, status ) ]
        self.changed()
