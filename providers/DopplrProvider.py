from Provider import *
import urllib
import re
import xmltramp
from datetime import datetime
from time import sleep, time, strftime, gmtime

from Utilities import _info

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
        
        try:
            url = "https://www.dopplr.com/api/traveller_info.xml?token=%s&traveller=%s"%( self.token, self.username )
            xml = self.cacheUrl( url, timeout = 3600 * 2 )
            print(xml)
            doc = xmltramp.parse( xml )
            doc.traveller.status
        except AttributeError:
            return # no service?
        
        if not doc:
            self.atoms = []
            self.changed()
            return
        
        # dopplr api coveniently provides offset from UTC :-)
        seconds = int(str(doc.traveller.current_city.utcoffset))

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
            self.atoms[2] = "<p class='time'>Time in %s is %s.</p>"%(
                doc.traveller.current_city.country,
                strftime("%a&nbsp;%l:%M&nbsp;%p", gmtime(epoch))
            )
            self.changed()
            sleep(20)

