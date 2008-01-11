from Provider import *
import urllib
import re
import xmltramp
from datetime import datetime
from time import sleep, time, strftime, gmtime

class DopplrProvider( Provider ):

    def provide( self ):
        self.token = NSUserDefaults.standardUserDefaults().stringForKey_("dopplrToken")
        dopplrs = self.person.takeUrls(r'dopplr\.com/traveller')
        if not dopplrs or not self.token: return
    
        self.username = re.search(r'/traveller/([^/]+)', dopplrs[0]).group(1)
        self.atoms = [ "<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a>&nbsp;%s</h3>"%( self.username, self.spinner() ) ]
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
        seconds = int( offset[1:3] ) * 3600 + int( offset[4:6] ) * 60
        if offset[0] != '+':
            seconds = -1 * seconds
            

        self.atoms = []
        self.atoms.append("<h3><a href='http://www.dopplr.com/traveller/%s/'>Dopplr</a></h3>"%( self.username ))
        self.atoms.append("<p>%s %s.</p>"%(
            self.person.displayName(),
            doc.traveller.status
        ))
        self.atoms.append("")
        
        self.changed()
        
        while self.running:
            epoch = time() + seconds
            self.atoms[2] = "<p>Time in %s is %s&nbsp;(%s).</p>"%(
                doc.traveller.current_city.country,
                strftime("%a&nbsp;%l:%M&nbsp;%p", gmtime(epoch)),
                offset
            )
            self.changed()
            sleep(20)

